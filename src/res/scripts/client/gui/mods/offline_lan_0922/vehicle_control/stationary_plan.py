"""Player-local, motion-only stationary firing-pose plans.

Projected poses never authorize fire. Actual muzzle, geometry and armour
remain the independent first-trigger admission boundary.

This is a sufficient, sampled-native-support planning certificate, not an
exhaustive search of every yaw or a new terrain model.  The original complete
collision arc, peer contact law and arena envelope are retained.  Native
support is independently sampled at the source and at each collision slice's
middle/end. Hydraulic players use the chassis contact solver from the local
physics path. Missing or unreachable support stays pending.
"""
from __future__ import division

import math

from .actor_observation import observation
from ..native_input_diagnostics import combat_detail, combat_detail_enabled
import time

from .. import arena_boundary, ballistics, shot_geometry, tank_collision, vehicle_physics
from ..gun_mechanics import _field
from .geometry import DESTRUCTIBLE_POSE_MAX_ANGLE_STEP
from .native_aim import (mechanical_reach, NATIVE_ANGLE_TOLERANCE,
                         active_hydraulic_pose, hydraulic_body, hydraulic_reach)
from .stationary_scope import _finite, _native_motion, _point


SLICES_PER_TICK = 4
SUPPORT_SAMPLES_PER_TICK = 12
WALL_SECONDS_PER_TICK = .004
PROJECTION_ITERATIONS = 12
_POSITION_EPSILON = .0001
_PEER_DEPENDENCY = 11
_SUPPORT_DEPENDENCY = 14
_WALL_CLOCK = getattr(time, 'perf_counter', time.time)
_DEPENDENCY_NAMES = ('weapon', 'planning_pose', 'position', 'native_position',
    'scene', 'motion', 'pivot', 'mounted_box', 'bounds', 'shape', 'rotation_limit',
    'peers', 'sensor', 'collision', 'support', 'debris', 'hydraulic')


def plan_diagnostic(row):
    """Read only the opt-in identity; it never constitutes planning evidence."""
    plan = (row or {}).get('stationary_plan') or {}
    proof = plan.get('proof') or {}
    return proof.get('diagnostic') or (row or {}).get('stationary_diagnostic')


def trace_plan_use(runtime, phase, row, now, reason, **details):
    if not combat_detail_enabled():
        return
    def payload():
        policy = getattr(runtime, 'attack_policy', None)
        combat = getattr(runtime, 'combat_stop', None)
        state = runtime.state or {}
        selected = (getattr(policy, 'decision', None) or {}).get('candidate') or {}
        pivot = getattr(combat, 'pivot', None) or {}
        result = dict(checked_key=(row or {}).get('key'), plan=plan_diagnostic(row),
            selected_key=selected.get('key'), pivot_key=pivot.get('key'),
            loaded=(getattr(policy, 'frame', None) or {}).get('loaded'),
            line=(row or {}).get('line'), armor=(row or {}).get('armor'),
            mechanical=(row or {}).get('mechanical'),
            point=((row or {}).get('solution') or {}).get('point'),
            yaw=state.get('yaw'), position=state.get('position'),
            siege_state=state.get('siege_state'))
        result.update(details)
        return result
    combat_detail(runtime, 'stationary_' + phase, runtime.actor_id, now, reason,
                  payload)


def _angle(value):
    return (float(value) + math.pi) % (2. * math.pi) - math.pi


def _same_point(first, second, tolerance):
    return all(abs(a - b) <= tolerance for a, b in zip(first, second))


def _support_stamp(physical):
    plane = physical.support_plane()
    values = None
    if isinstance(plane, dict):
        values = tuple((name, None if plane.get(name) is None else
            _point(plane[name]) if name == 'normal' else _finite(plane[name]))
            for name in ('center_y', 'normal', 'pitch', 'roll',
                         'gradient_x', 'gradient_z', 'residual'))
    return bool(getattr(physical, 'complete_support', lambda: False)()), values


def _same_support_stamp(first, second):
    if first[0] != second[0] or first[1] is None or second[1] is None:
        return first == second
    for (name, before), (other, after) in zip(first[1], second[1]):
        if name != other or before is None or after is None:
            if name != other or before != after:
                return False
            continue
        tolerance = _POSITION_EPSILON if name in ('center_y', 'residual') else NATIVE_ANGLE_TOLERANCE
        if name == 'residual' and (before <= _POSITION_EPSILON) != (after <= _POSITION_EPSILON):
            return False
        if not (_same_point(before, after, tolerance) if name == 'normal'
                else abs(before - after) <= tolerance):
            return False
    return True


def _pending(reason, progressing=False):
    return dict(status='pending', proved=False, reason=reason,
                progressing=bool(progressing))


def _box(value):
    low, high = _point(value[0]), _point(value[1])
    if any(low[axis] >= high[axis] for axis in range(3)):
        raise ValueError('native body box is unavailable')
    return low, high


def _pivot(descriptor, runtime):
    around = _field(_field(descriptor, 'chassis'), 'rotationIsAroundCenter')
    if isinstance(around, bool):
        if around:
            return dict(rotationIsAroundCenter=True)
        params = vehicle_physics.track_pivot_descriptor_params(descriptor)
    else:
        installed = observation(runtime).physical_params()
        params = None
        if isinstance(installed, dict) and isinstance(
                installed.get('rotationIsAroundCenter'), bool):
            params = dict(rotationIsAroundCenter=installed['rotationIsAroundCenter'])
            if not params['rotationIsAroundCenter']:
                # World rotation takes an explicit pivot, but the original
                # catalogue/tree sweep independently recovers its trajectory
                # from this descriptor. A private physics-only gauge cannot
                # establish the same arc for all three native consumers.
                raise ValueError('track pivot descriptor contract is incomplete')
    if (not isinstance(params, dict) or (not params['rotationIsAroundCenter'] and
            not 0. < _finite(params.get('trackCenter')) <= 100.)):
        raise ValueError('native stationary pivot law is unavailable')
    return params


class _EngineView(object):
    """Only a private observation overlay; the real actor is never edited."""
    def __init__(self, engine, actor, state):
        self.original = engine
        self.states = dict(engine.states)
        self.states[actor] = state

    def __getattr__(self, name):
        return getattr(self.original, name)


class _SensorView(object):
    """Retain raw tree evidence before the native motion compatibility seam."""
    def __init__(self, sensor):
        self.original, self.tree_receipt = sensor, None

    def __getattr__(self, name):
        return getattr(self.original, name)

    def _tree_motion_proposal(self, *args, **kwargs):
        self.tree_receipt = self.original._tree_motion_proposal(*args, **kwargs)
        return self.tree_receipt


def _geometry_view(runtime, position, body):
    original = runtime.geometry
    view = object.__new__(type(original))
    view.__dict__.update(original.__dict__)
    state = dict(runtime.state)
    state.update(position=position, x=position[0], y=position[1], z=position[2],
                 yaw=body[0], pitch=body[1], terrain_pitch=body[1], roll=body[2],
                 grounded_once=True, airborne=False, movement_dir=0,
                 rotation_dir=0)
    view._bots = _EngineView(runtime.engine, runtime.actor_id, state)
    view._destructibles = _SensorView(original._destructibles)
    view._bot_motion_kinds = {}
    view._bot_tree_contacts_pending = {}
    view._local_tree_diagnostics = None
    return view


class _Deferred(Exception):
    def __init__(self, reason, progressing=False):
        Exception.__init__(self, reason)
        self.reason, self.progressing = reason, progressing


class StationaryPlanner(object):
    def __init__(self, runtime):
        self.runtime = runtime
        self.clock = _WALL_CLOCK
        self._epoch = None
        self._epoch_serial = 0
        self._supports, self._arcs, self._plans = {}, {}, {}
        self._paths = {}
        self._budget_at = None
        self._work_frame = None
        self._slices, self._support_left = 0, 0
        self._deadline = 0.

    def _peers(self, position, radius):
        """Native bodies which can enter the whole stationary-turn envelope.

        Recompute membership on every check, including current() on an old
        frame. Far traffic does not retire completed static-world slices;
        a newly entering body cannot reuse their former peer clearance.
        """
        owner, result = self.runtime.owner, []
        for key, record in sorted(owner._records.items()):
            if observation(self.runtime).owns_record(record) or record.get('tombstone'):
                continue
            state = record.get('state') or {}
            same_team = int(record.get('team', state.get('team', 0))) == int(observation(self.runtime).actor_team)
            if not (same_team or record.get('spot_visible') or not state.get('alive', True)):
                continue
            entity = owner._server_entity(record.get('engine_id'))
            if not record.get('ready') or entity is None or not getattr(entity, 'isStarted', False):
                raise _Deferred('stationary_peer_geometry_pending')
            descriptor = entity.typeDescriptor
            for name in ('chassis', 'hull'):
                _box(_field(_field(descriptor, name), 'hitTester').bbox)
            matrix = owner._runtime.math.Matrix(entity.matrix)
            shape = tuple(_finite(value) for value in tank_collision.chassis_shape(descriptor))
            point = _point(matrix.translation)
            peer_radius = math.sqrt(shape[0] ** 2 + shape[1] ** 2 +
                                    max(abs(shape[2]), abs(shape[3])) ** 2)
            if math.hypot(point[0] - position[0], point[2] - position[2]) > (
                    radius + peer_radius + _POSITION_EPSILON):
                continue
            result.append(dict(id=record.get('engine_id'), key=key,
                position=point, yaw=_finite(matrix.yaw),
                pitch=_finite(matrix.pitch), roll=_finite(matrix.roll), shape=shape,
                descriptor=id(descriptor)))
        return tuple(result)

    def _dependencies(self, frame):
        runtime, owner, descriptor = self.runtime, self.runtime.owner, frame['descriptor']
        from .attack_policy import native_source_pose
        native_origin = _point(observation(runtime).mutable_shot_ray()[0])
        native_pose = native_source_pose(runtime, native_origin)
        if (any(native_pose[index] != frame['pose'][index] for index in (1, 2, 4, 5, 6)) or
                frame['identity'] != tuple(observation(runtime).weapon_identity()) + (id(descriptor.gun),)):
            error = _Deferred('stationary_native_source_changed')
            if combat_detail_enabled():
                error.diagnostic = dict(frame_pose=frame['pose'], native_pose=native_pose,
                    frame_identity=frame['identity'], native_identity=
                    tuple(observation(runtime).weapon_identity()) + (id(descriptor.gun),))
            raise error
        motion = _native_motion(runtime)
        state = runtime.state
        if (motion[1] or any(abs(value) > 1.e-6 for value in motion[2:5]) or
                not state.get('grounded_once') or
                state.get('_foreground_support_blocked') or
                observation(runtime).support_rise_blocked()):
            if combat_detail_enabled():
                combat_detail(runtime, 'stationary_motion_pending', runtime.actor_id,
                    runtime.now, 'stationary_native_support_unsettled', lambda: dict(
                        airborne=motion[1], speed=motion[2], turn_speed=motion[3],
                        vertical_speed=motion[4], siege_state=motion[5],
                        grounded_once=bool(state.get('grounded_once')),
                        foreground_blocked=bool(state.get('_foreground_support_blocked')),
                        rise_blocked=observation(runtime).support_rise_blocked(),
                        position=frame['position'], body=frame['body']))
            raise _Deferred('stationary_native_support_unsettled')
        if any('engine' in value.lower() or 'track' in value.lower() or
               'chassis' in value.lower() for value in motion[0]):
            raise _Deferred('stationary_rotation_actuator_unavailable')
        if motion[5] in (1, 3):
            raise _Deferred('stationary_mode_transition_pending')
        hydraulic = active_hydraulic_pose(runtime, frame)
        planning_pose = frame.get('planning_pose', frame['pose'])
        position, mounted_position = _point(frame['position']), _point(frame['pose'][6])
        old = self._epoch
        if hydraulic is not None and old is not None and old[-1] is not None:
            previous = dict(old[-1])
            if (planning_pose[2:] == old[1][2:] and
                    _same_point(planning_pose[0], old[1][0], NATIVE_ANGLE_TOLERANCE) and
                    _same_point(planning_pose[1], old[1][1], _POSITION_EPSILON) and
                    _same_point(position, old[2], _POSITION_EPSILON) and
                    _same_point(mounted_position, old[3], _POSITION_EPSILON) and
                    all(hydraulic[key] == previous.get(key) for key in hydraulic
                    if key not in ('body', 'position', 'correction')) and
                    abs(hydraulic['correction'] - previous['correction']) <= NATIVE_ANGLE_TOLERANCE and
                    _same_point(hydraulic['body'], previous['body'], NATIVE_ANGLE_TOLERANCE) and
                    _same_point(hydraulic['position'], previous['position'], _POSITION_EPSILON)):
                planning_pose, position, mounted_position = old[1:4]
                hydraulic = previous
        hydraulic_stamp = tuple(sorted(hydraulic.items())) if hydraulic is not None else None
        pivot = _pivot(descriptor, runtime)
        for name in ('chassis', 'hull', 'turret', 'gun'):
            _box(_field(_field(descriptor, name), 'hitTester').bbox)
        sensor = getattr(runtime.geometry, '_destructibles', None)
        reader = getattr(sensor, '_vehicle_body_bbox', None)
        if not callable(reader):
            reader = getattr(sensor, '_vehicle_hull_bbox', None)
        if (not callable(reader) or not callable(getattr(sensor, '_catalog_motion_proposal', None)) or
                not callable(getattr(sensor, '_tree_motion_proposal', None)) or
                not callable(getattr(owner._runtime.bigworld, 'wg_collideSegment', None))):
            raise _Deferred('stationary_native_collision_contract_unavailable')
        mounted_box = _box(reader(descriptor))
        revision = getattr(sensor, '_spatial_revision_1513', None)
        if not callable(revision):
            raise _Deferred('stationary_native_scene_revision_unavailable')
        native_scene = (id(owner._avatar), owner._avatar.spaceID, revision())
        native_support = _support_stamp(observation(runtime))
        if old is not None and _same_support_stamp(old[_SUPPORT_DEPENDENCY], native_support):
            # Use the same existing native precision as the source-pose
            # anchor. Compare to that anchor, never to the preceding sample,
            # so a real accumulated support change still retires all work.
            native_support = old[_SUPPORT_DEPENDENCY]
        bounds = tuple(_finite(value) for value in runtime.geometry._arena_bounds)
        if not arena_boundary.valid(bounds):
            raise _Deferred('stationary_arena_bounds_unavailable')
        shape = tuple(_finite(value) for value in state['collision_shape'])
        if len(shape) != 4 or shape[0] <= 0. or shape[1] <= 0. or shape[2] >= shape[3]:
            raise ValueError('native collision shape is unavailable')
        # One sphere encloses every yaw and either native stationary track
        # pivot. It is only a conservative peer-membership broad phase, not
        # a replacement for the original exact rotating contact predicate.
        radius = max(math.sqrt(sum(max(abs(mounted_box[0][axis]),
            abs(mounted_box[1][axis])) ** 2 for axis in range(3))),
            math.sqrt(shape[0] ** 2 + shape[1] ** 2 + max(abs(shape[2]), abs(shape[3])) ** 2))
        radius += math.sqrt(sum((native_pose[6][axis] - native_pose[0][axis]) ** 2
                                for axis in range(3)))
        if not pivot['rotationIsAroundCenter']:
            radius += 2. * pivot['trackCenter']
        peers = self._peers(native_pose[0], radius)
        debris = getattr(owner, '_detached_turret_obstacles', None)
        debris_stamp = None
        if debris is not None:
            ready = getattr(debris, '_ready', None)
            if not callable(ready):
                raise _Deferred('stationary_detached_turret_geometry_pending')
            relevant = []
            for turret in ready(runtime.geometry._turret_server_time_ms()):
                rest, turret_radius = _point(turret['rest']), _finite(turret['radius'])
                if turret_radius < 0.:
                    raise ValueError('native detached turret radius is invalid')
                if math.hypot(rest[0] - native_pose[0][0], rest[2] - native_pose[0][2]) <= (
                        radius + turret_radius + _POSITION_EPSILON):
                    row = turret['row']
                    relevant.append((row['actor_kind'], row['actor_id'], row.get('motion_seq', 0),
                        rest, _point(turret['attitude']), turret_radius,
                        'body' in row['flight']))
            debris_stamp = id(debris), tuple(sorted(relevant))
        peer_stamp = tuple((p['key'], p['position'], p['yaw'], p['pitch'], p['roll'],
                           p['shape'], p['descriptor']) for p in peers)
        params = runtime.engine._physics_params_for(runtime.actor_id)
        cap = _finite(params['rotSpd'])
        if cap <= 0.:
            raise _Deferred('stationary_rotation_actuator_unavailable')
        return (frame['identity'], planning_pose, position, mounted_position,
                frame.get('scene'), motion,
                tuple(sorted(pivot.items())), mounted_box, bounds, shape, cap,
                peer_stamp, id(sensor), native_scene, native_support, debris_stamp,
                hydraulic_stamp), pivot, peers, cap

    def _budget(self, now, deadline):
        frame = now if self._work_frame is None else self._work_frame
        if self._budget_at != frame:
            self._budget_at = frame
            self._slices, self._support_left = SLICES_PER_TICK, SUPPORT_SAMPLES_PER_TICK
            self._deadline = self.clock() + WALL_SECONDS_PER_TICK
        limit = self._deadline if deadline is None else min(self._deadline, deadline)
        if self.clock() >= limit:
            raise _Deferred('stationary_probe_budget_pending', True)
        return limit

    def _support(self, frame, position, yaw, now, deadline, chassis=None,
                 maximum_y=None):
        key = tuple(position), float(yaw), maximum_y
        if key not in self._supports:
            self._budget(now, deadline)
            if self._support_left <= 0:
                raise _Deferred('stationary_probe_budget_pending', True)
            self._support_left -= 1
            if chassis is not None:
                trace = [] if combat_detail_enabled() else None
                plane = chassis(position, yaw, frame['descriptor'], maximum_y, trace)
                if trace is not None:
                    reason = 'supported' if plane is not None else 'unavailable'
                    combat_detail(self.runtime, 'stationary_chassis_support',
                        self.runtime.actor_id, now, reason,
                        lambda: dict(position=position, yaw=yaw, ceiling=maximum_y,
                                     support=plane, columns=trace))
                if plane is None:
                    raise _Deferred('stationary_native_support_pending')
                posed = (position[0], _finite(plane['center_y']), position[2])
                self._supports[key] = dict(plane, position=posed, yaw=float(yaw))
                return self._supports[key]
            geometry = self.runtime.geometry
            samples, ground_probe = None, None
            if combat_detail_enabled():
                samples = []

                def ground_probe(x, z, hint):
                    height = geometry._ground_y(x, z, hint)
                    samples.append((x, z, height))
                    return height

            plane = geometry._sample_ground_plane(position, yaw, frame['descriptor'], ground_probe)
            if not isinstance(plane, dict):
                if samples is not None:
                    combat_detail(self.runtime, 'stationary_support_plane',
                        self.runtime.actor_id, now, 'sample_plane_unavailable',
                        lambda: dict(position=position, yaw=yaw, samples=samples))
                raise _Deferred('stationary_native_support_pending')
            # The original sampler's broad residual accepts drivable steps;
            # those are not evidence for transporting this exact plane.
            residual = _finite(plane['residual'])
            if residual > _POSITION_EPSILON:
                if samples is not None:
                    combat_detail(self.runtime, 'stationary_support_plane',
                        self.runtime.actor_id, now, 'sample_fit_residual',
                        lambda: dict(position=position, yaw=yaw, residual=residual,
                                     position_tolerance=_POSITION_EPSILON,
                                     center_y=plane.get('center_y'), normal=plane.get('normal'),
                                     samples=samples))
                raise _Deferred('stationary_support_plane_changes')
            plane = dict(plane, position=tuple(position), yaw=float(yaw))
            self._supports[key] = plane
        return self._supports[key]

    def _same_support(self, source, plane, now):
        predicted_y = (source['center_y'] + source['gradient_x'] *
            (plane['position'][0] - source['position'][0]) + source['gradient_z'] *
            (plane['position'][2] - source['position'][2]))
        height_error = _finite(plane['center_y']) - predicted_y
        if (abs(height_error) > _POSITION_EPSILON or
                any(abs(_finite(plane['normal'][axis]) - _finite(source['normal'][axis])) >
                    NATIVE_ANGLE_TOLERANCE for axis in range(3))):
            if combat_detail_enabled():
                combat_detail(self.runtime, 'stationary_support_plane',
                    self.runtime.actor_id, now, 'transported_plane_mismatch',
                    lambda: dict(source_position=source['position'], source_yaw=source['yaw'],
                        position=plane['position'], yaw=plane['yaw'], predicted_y=predicted_y,
                        sampled_y=plane['center_y'], height_error=height_error,
                        source_normal=source['normal'], normal=plane['normal'],
                        position_tolerance=_POSITION_EPSILON,
                        normal_tolerance=NATIVE_ANGLE_TOLERANCE))
            raise _Deferred('stationary_support_plane_changes')
        # The existing rotation resolver transports X/Z, not a vertical
        # suspension path. A track pivot climbing a slope needs that owner.
        if abs(plane['center_y'] - source['center_y']) > _POSITION_EPSILON:
            raise _Deferred('stationary_track_vertical_path_pending')

    def _project_point(self, frame, shell, target, raw, pivot, hydraulic=None,
                       support_at=None):
        descriptor, position, body = frame['descriptor'], _point(frame['position']), _point(frame['body'])
        mounted_position = _point(frame['pose'][6])
        displacement = tuple(mounted_position[i] - position[i] for i in range(3))
        native_model, unused = shot_geometry.shot_origin_and_direction(
            descriptor, mounted_position, body[0], body[1], body[2], frame['pose'][3][0], 0.)
        if any(abs(native_model[i] - frame['origin'][i]) > _POSITION_EPSILON for i in range(3)):
            raise _Deferred('stationary_native_origin_model_pending')
        sample, velocity = _point(raw['sample_point']), _point(target['velocity'])
        speed, gravity, maximum = (_finite(_field(shell['shot'], name))
                                   for name in ('speed', 'gravity', 'maxDistance'))
        gravity = abs(gravity)
        if speed <= 1. or gravity <= .01 or maximum <= 0.:
            raise ValueError('native ballistics are unavailable')
        limits = _field(_field(descriptor, 'gun'), 'turretYawLimits')
        low, high = (-math.pi, math.pi) if limits is None else tuple(_finite(v) for v in limits)
        if not -math.pi <= low <= high <= math.pi:
            raise ValueError('native yaw limits are unavailable')
        # A target-centre heading shares the safe arc between its samples.
        # A zero-width gun may require further bounded point-specific turns.
        centre = _point(target['matrix'].translation)
        support_body = hydraulic['body'] if hydraulic is not None else body
        yaw = math.atan2(centre[0] - position[0], centre[2] - position[2])
        correction = hydraulic['correction'] if hydraulic is not None else 0.
        flat_offset = (shot_geometry.inverse_transform_vehicle_vector(
            tuple(hydraulic['position'][i] - position[i] for i in range(3)), *support_body)
            if hydraulic is not None else None)
        turret, previous = min(high, max(low, 0.)), None
        for unused in range(PROJECTION_ITERATIONS):
            delta = _angle(yaw - support_body[0])
            offset = vehicle_physics.track_pivot_offset(pivot, 0., delta)
            projected_position = vehicle_physics.track_pivot_position(position, support_body[0], yaw, offset)
            if support_at is not None:
                support = support_at(projected_position, yaw)
                projected_position = support['position']
                pitch, roll = support['pitch'], support['roll']
            else:
                pitch, roll = vehicle_physics.ground_pose_for_yaw(
                    support_body[1], support_body[2], support_body[0], yaw)
            projected_body = (yaw, pitch, roll)
            flat_body = projected_body
            base = tuple(projected_position[i] + displacement[i] for i in range(3))
            if hydraulic is not None:
                flat_position = shot_geometry.transform_vehicle_point(
                    flat_offset, projected_position, *flat_body)
                base, projected_body = hydraulic_body(
                    flat_position, flat_body, correction, hydraulic['centerZ'])
            origin, unused_direction = shot_geometry.shot_origin_and_direction(
                descriptor, base, projected_body[0], projected_body[1], projected_body[2], turret, 0.)
            solved = ballistics.ballistic_intercept(origin, sample, velocity, speed, gravity)
            if solved is None or solved[2] * speed > maximum + 1.e-6:
                raise _Deferred('stationary_projected_intercept_pending')
            aim, gun_pitch, flight = solved
            gun_yaw = math.atan2(aim[0] - origin[0], aim[2] - origin[2])
            direction = (math.sin(gun_yaw) * math.cos(gun_pitch), -math.sin(gun_pitch),
                         math.cos(gun_yaw) * math.cos(gun_pitch))
            reach = mechanical_reach(descriptor, direction, projected_body)
            next_correction = correction
            if hydraulic is not None:
                active = hydraulic_reach(descriptor, direction, flat_body, hydraulic)
                if not active.get('reachable') and not active.get('needs_hull'):
                    raise _Deferred('stationary_hydraulic_pitch_unreachable')
                next_correction = active['hydraulic_pitch']
                reach = dict(reach, local_yaw=active['local_yaw'])
            following_turret = min(high, max(low, reach['local_yaw']))
            error = _angle(reach['local_yaw'] - following_turret)
            following_yaw = _angle(yaw + error)
            if (previous is not None and abs(error) < 1.e-7 and
                    abs(_angle(following_turret - turret)) < 1.e-7 and
                    abs(next_correction - correction) < 1.e-7 and
                    sum((origin[i] - previous[i]) ** 2 for i in range(3)) < 1.e-12):
                if not reach['reachable']:
                    if combat_detail_enabled():
                        combat_detail(self.runtime, 'stationary_endpoint_rejected',
                            self.runtime.actor_id, frame['observed_at'],
                            (shell['index'], target['key'], raw.get('sample')),
                            lambda: dict(target=target['key'], sample=sample,
                                source_position=position, source_body=body,
                                projected_position=projected_position,
                                flat_body=flat_body, projected_body=projected_body,
                                origin=origin, direction=direction, reach=reach,
                                active_reach=active if hydraulic is not None else None,
                                correction=correction, next_correction=next_correction,
                                turret=turret, following_turret=following_turret,
                                tags=tuple(sorted(_field(_field(descriptor, 'type'), 'tags', ()) or ()))))
                    raise _Deferred('stationary_projected_pitch_pending')
                path = ballistics.ballistic_path(origin, gun_yaw, gun_pitch, speed, gravity, flight)
                solution = dict(raw.get('solution') or {})
                solution.update(point=tuple(aim), aim_position=tuple(aim), source_point=tuple(aim),
                    yaw=gun_yaw, pitch=gun_pitch, direction=direction, origin=origin,
                    flight_time=flight, path=path, reachable=True,
                    needs_hull=abs(delta) > NATIVE_ANGLE_TOLERANCE,
                    hull_yaw=yaw, body=projected_body, position=projected_position,
                    stationary_plan=True, source_verified=False, mechanical_reason='stationary_plan')
                if hydraulic is not None:
                    solution.update(hydraulic_pitch=correction, siege_correction=correction,
                        needs_hydraulic=abs(correction - hydraulic['correction']) > NATIVE_ANGLE_TOLERANCE,
                        flat_body=flat_body, flat_position=flat_position)
                projected = dict(frame, position=projected_position, body=projected_body, origin=origin)
                return dict(projected_frame=projected, pivot_offset=offset,
                    flat_body=flat_body, hydraulic_pitch=correction,
                    prediction=dict(path=path, reach=dict(reach, status='reachable'),
                        solution=solution, sample_point=sample, direction=direction, flight=flight))
            previous, yaw, turret, correction = origin, following_yaw, following_turret, next_correction
        raise _Deferred('stationary_projection_unsettled')

    def _hydraulic_pose(self, frame, position, body, hydraulic, correction):
        # Native hydraulic contact uses a flat chassis and a separately
        # pivoted hull. Match that consumer instead of tilting the terrain.
        offset = shot_geometry.inverse_transform_vehicle_vector(
            tuple(hydraulic['position'][i] - frame['position'][i] for i in range(3)),
            *hydraulic['body'])
        base = shot_geometry.transform_vehicle_point(offset, position, *body)
        mounted, actual = hydraulic_body(base, body, correction, hydraulic['centerZ'])
        pose = dict(x=position[0], y=position[1], z=position[2],
                    yaw=body[0], pitch=body[1], roll=body[2],
                    actor_key=observation(self.runtime).own_record_key)
        pose['hull'] = dict(x=mounted[0], y=mounted[1], z=mounted[2],
                           yaw=actual[0], pitch=actual[1], roll=actual[2])
        return pose

    def _hydraulic_sweep(self, frame, before_position, before_body, before_correction,
                         after_position, after_body, after_correction, hydraulic):
        probe = getattr(self.runtime.geometry, '_turret_motion_is_clear', None)
        if not callable(probe):
            raise _Deferred('stationary_hydraulic_native_sweep_unavailable')
        before = self._hydraulic_pose(frame, before_position, before_body, hydraulic, before_correction)
        after = self._hydraulic_pose(frame, after_position, after_body, hydraulic, after_correction)
        clear = probe(before, after, frame['descriptor'])
        if clear is not True:
            raise _Deferred('stationary_hydraulic_sweep_blocked' if clear is False else
                            'stationary_hydraulic_sweep_pending')
        return dict(before=before, after=after, native_clear=True)

    def _chassis_step(self, frame, position, yaw, previous, cap, now, deadline, chassis):
        plane = self._support(frame, position, yaw, now, deadline, chassis)
        height = previous['center_y']
        # A stopped chassis uses the legacy rise limit. A higher hit may
        # cover a valid lower floor, so retry the same five columns below it.
        if tank_collision.support_rise_is_obstacle(height, plane['center_y'], .6):
            plane = self._support(frame, position, yaw, now, deadline, chassis, height + .62)
        dt = abs(_angle(yaw - previous['yaw'])) / cap
        if not vehicle_physics.ground_reachable(height, plane['center_y'], 0., dt):
            raise _Deferred('stationary_chassis_support_drop')
        return plane

    def _slice(self, frame, source, first, last, offset, peers, cap, now, deadline,
               hydraulic=None, chassis=None, preceding=None):
        key = (float(first), float(last), float(offset),
               preceding['center_y'] if preceding is not None else None)
        position, body = _point(frame['position']), _point(frame['body'])
        start = vehicle_physics.track_pivot_position(position, body[0], first, offset)
        shape = tuple(self.runtime.state['collision_shape'])
        if preceding is None:
            fraction = tank_collision.rotation_fraction(start, first, last, shape, peers,
                                                         pivot_offset=offset)
            if _finite(fraction) < 1.:
                raise _Deferred('stationary_peer_rotation_blocked')
        if key in self._arcs:
            receipt = self._arcs[key]
            observations = receipt['support']
        else:
            self._budget(now, deadline)
            if self._slices <= 0:
                raise _Deferred('stationary_probe_budget_pending', True)
            middle = first + _angle(last - first) * .5
            observations = []
            previous = preceding
            for angle in (middle, last):
                at = vehicle_physics.track_pivot_position(position, body[0], angle, offset)
                if chassis is None:
                    plane = self._support(frame, at, angle, now, deadline)
                    self._same_support(source, plane, now)
                else:
                    probe = (at[0], previous['center_y'], at[2])
                    plane = self._chassis_step(
                        frame, probe, angle, previous, cap, now, deadline, chassis)
                    previous = plane
                observations.append(plane)
        arc = (preceding,) + tuple(observations) if chassis is not None else None
        if arc is not None:
            start = preceding['position']
            low = min(pose['center_y'] for pose in arc) - start[1]
            high = max(pose['center_y'] for pose in arc) - start[1]
            shape = (shape[0], shape[1], shape[2] + low, shape[3] + high)
            fraction = tank_collision.rotation_fraction(start, first, last, shape, peers,
                                                         pivot_offset=offset)
            if _finite(fraction) < 1.:
                raise _Deferred('stationary_peer_rotation_blocked')
        if key in self._arcs:
            return receipt
        bounds = tuple(self.runtime.geometry._arena_bounds)
        swept = vehicle_physics.track_pivot_sweep_bounds(start, first, last, offset, shape[0], shape[1])
        if (swept[0] < bounds[0] or swept[1] < bounds[1] or
                swept[2] > bounds[2] or swept[3] > bounds[3]):
            raise _Deferred('stationary_arena_rotation_blocked')
        self._budget(now, deadline)
        self._slices -= 1
        if arc is not None:
            pitch, roll = preceding['pitch'], preceding['roll']
            endpoint = observations[-1]['position']
        else:
            pitch, roll = vehicle_physics.ground_pose_for_yaw(body[1], body[2], body[0], first)
            endpoint = vehicle_physics.track_pivot_position(start, first, last, offset)
        view = _geometry_view(self.runtime, start, (first, pitch, roll))
        if not self.runtime.engine._turret_pose_is_clear(
                view._bots.states[self.runtime.actor_id], start, first, endpoint, last):
            raise _Deferred('stationary_detached_turret_rotation_blocked')
        hydraulic_receipt = None
        if hydraulic is not None:
            if arc is None:
                final_pitch, final_roll = vehicle_physics.ground_pose_for_yaw(
                    body[1], body[2], body[0], last)
                hydraulic_receipt = self._hydraulic_sweep(frame, start, (first, pitch, roll),
                    hydraulic['correction'], endpoint, (last, final_pitch, final_roll),
                    hydraulic['correction'], hydraulic)
            else:
                correction = hydraulic['correction']
                sweeps = tuple(self._hydraulic_sweep(frame,
                    before['position'], (before['yaw'], before['pitch'], before['roll']), correction,
                    after['position'], (after['yaw'], after['pitch'], after['roll']), correction,
                    hydraulic) for before, after in zip(arc, arc[1:]))
                hydraulic_receipt = dict(before=sweeps[0]['before'],
                    middle=sweeps[0]['after'], after=sweeps[-1]['after'], native_clear=True)
        clear = view._resolve_bot_rotation(self.runtime.actor_id, start, first, last,
            frame['descriptor'], max(1.e-6, abs(_angle(last - first)) / cap), now,
            cap, pivot_offset=offset, commit_enabled=False, support_arc=arc)
        if clear is not True:
            if arc is not None and combat_detail_enabled():
                contact = view._bots.states[self.runtime.actor_id].get('_rotation_contact_trace')
                combat_detail(self.runtime, 'stationary_chassis_rotation',
                    self.runtime.actor_id, now, 'collision_pending' if clear is None else 'collision',
                    lambda: dict(start=start, from_yaw=first, to_yaw=last, contact=contact))
            raise _Deferred('stationary_native_rotation_pending' if clear is None else
                            'stationary_native_rotation_blocked')
        tree = view._destructibles.tree_receipt
        if (not isinstance(tree, dict) or tree.get('status') not in ('clear', 'crushed') or
                tree.get('requires_commit')):
            raise _Deferred('stationary_native_tree_contact_pending')
        receipt = dict(start=start, start_yaw=first, end_yaw=last, pivot_offset=offset,
                       support=tuple(observations), peer_fraction=fraction,
                       arena_envelope=swept, native_clear=True, tree=dict(tree),
                       hydraulic=hydraulic_receipt)
        self._arcs[key] = receipt
        return receipt

    def _path_support(self, frame, source, yaw, offset, peers, cap, now,
                      deadline, hydraulic, chassis, receipts):
        """One checked support history for endpoint aiming and turn admission.

        Prefixes only survive identical scene/peer/source dependencies. Every
        new segment still uses the original complete support/collision slice.
        Unfinished work resumes at its first missing segment, not segment zero.
        """
        delta = _angle(yaw - frame['body'][0])
        sign = 1. if delta >= 0. else -1.
        step = DESTRUCTIBLE_POSE_MAX_ANGLE_STEP
        count = int(math.floor(abs(delta) / step))
        key = float(offset), sign
        path = self._paths.setdefault(key, dict(poses=[source], arcs=[]))
        receipts[:] = path['arcs'][:count]
        while len(path['arcs']) < count:
            index = len(path['arcs'])
            first = frame['body'][0] + sign * step * index
            last = frame['body'][0] + sign * step * (index + 1)
            receipt = self._slice(frame, source, first, last, offset,
                peers, cap, now, deadline, hydraulic, chassis, path['poses'][-1])
            path['arcs'].append(receipt)
            path['poses'].append(receipt['support'][-1])
            receipts.append(receipt)
        endpoint = path['poses'][count]
        if abs(delta) - count * step > 1.e-9:
            first = frame['body'][0] + sign * step * count
            receipt = self._slice(frame, source, first, frame['body'][0] + delta,
                offset, peers, cap, now, deadline, hydraulic, chassis, endpoint)
            receipts.append(receipt)
            endpoint = receipt['support'][-1]
        return endpoint

    def project(self, frame, shell, target, raw_prediction, now, channel,
                deadline=None, diagnostic_key=None):
        receipts = []
        costs = {} if combat_detail_enabled() else None
        started = self.clock() if costs is not None else None
        try:
            begin = getattr(self.runtime.engine, '_begin_evaluation_frame', None)
            budget = begin(now) if callable(begin) else None
            self._work_frame = budget.frame if budget is not None else None
            if budget is not None and not budget.stationary(self.runtime.actor_id):
                raise _Deferred('stationary_shared_budget_pending')
            # An expired callback cannot gather the same dependencies again.
            # Open a fresh native-work quantum after gathering them below:
            # otherwise a slow dependency read can prevent the first native
            # slice on every callback, rather than merely bounding its work.
            work_frame = now if self._work_frame is None else self._work_frame
            if self._budget_at == work_frame:
                self._budget(now, deadline)
            dependencies, pivot, peers, cap = self._dependencies(frame)
            if costs is not None:
                costs['dependencies_ms'] = (self.clock()-started)*1000.
            if dependencies != self._epoch:
                if self._epoch is not None and combat_detail_enabled():
                    changed = tuple(name for name, before, after in
                                    zip(_DEPENDENCY_NAMES, self._epoch, dependencies) if before != after)
                    combat_detail(self.runtime, 'stationary_dependency_reset',
                        self.runtime.actor_id, now, changed,
                        lambda: dict(fields=changed, epoch=self._epoch_serial,
                                     support=len(self._supports), arcs=len(self._arcs),
                                     plans=len(self._plans),
                                     support_before=self._epoch[_SUPPORT_DEPENDENCY]
                                         if 'support' in changed else None,
                                     support_after=dependencies[_SUPPORT_DEPENDENCY]
                                         if 'support' in changed else None))
                peer = _PEER_DEPENDENCY
                if (self._epoch is None or self._epoch[:peer] != dependencies[:peer] or
                        self._epoch[peer + 1:] != dependencies[peer + 1:]):
                    self._supports, self._arcs = {}, {}
                self._epoch = dependencies
                self._epoch_serial += 1
                self._plans = {}
                self._paths = {}
            key = (shell['signature'], target['key'], target['pose'], target['velocity'],
                   tuple(raw_prediction['sample_point']))
            # Far moving targets no longer restart static arc work. Their
            # obsolete point plans still have a bounded per-target lifetime.
            for old_key in list(self._plans):
                if old_key[1] == key[1] and (old_key[2:4] != key[2:4] or
                        old_key[0][0] == key[0][0] and old_key[0] != key[0]):
                    self._plans.pop(old_key, None)
            if key in self._plans:
                return self._plans[key]
            self._budget(now, deadline)
            hydraulic = dict(dependencies[-1]) if dependencies[-1] is not None else None
            planned = frame
            if frame.get('stable_planning_pose'):
                planned = dict(frame, body=dependencies[1][0], origin=dependencies[1][1],
                    position=dependencies[2], pose=frame['pose'][:6] + (dependencies[3],))
            support_frame = dict(planned, body=hydraulic['body']) if hydraulic is not None else planned
            support_body = support_frame['body']
            physical = observation(self.runtime)
            complete = getattr(physical, 'complete_support', lambda: False)()
            # The physical owner supplies both its five-contact and complete
            # support proof. Mode changes must not select the unrelated strict
            # coplanar sampler while that same chassis is using basic contacts.
            owns_contacts = hydraulic or complete or getattr(self.runtime, 'actor_kind', 'human') == 'bot'
            chassis = getattr(physical, 'chassis_support_at', None) if owns_contacts else None
            if chassis is None:
                proposal = self._project_point(planned, shell, target, raw_prediction, pivot, hydraulic)
            source = self._support(support_frame, support_frame['position'], support_body[0],
                                   now, deadline, chassis)
            if (abs(source['pitch'] - support_body[1]) > NATIVE_ANGLE_TOLERANCE or
                    abs(source['roll'] - support_body[2]) > NATIVE_ANGLE_TOLERANCE or
                    chassis is not None and abs(source['center_y'] - planned['position'][1]) > _POSITION_EPSILON):
                raise _Deferred('stationary_source_support_disagrees')

            if chassis is not None:
                def support_at(position, yaw):
                    delta = _angle(yaw - support_body[0])
                    offset = vehicle_physics.track_pivot_offset(pivot, 0., delta)
                    return self._path_support(support_frame, source, yaw, offset,
                        peers, cap, now, deadline, hydraulic, chassis, receipts)

                proposal = self._project_point(planned, shell, target, raw_prediction,
                                               pivot, hydraulic, support_at)
            if costs is not None:
                costs['aim_and_support_ms'] = (self.clock()-started)*1000.-costs['dependencies_ms']
            delta = _angle(proposal['flat_body'][0] - support_body[0])
            sign = 1. if delta >= 0. else -1.
            count = int(math.floor(abs(delta) / DESTRUCTIBLE_POSE_MAX_ANGLE_STEP))
            angles = [support_body[0] + sign * DESTRUCTIBLE_POSE_MAX_ANGLE_STEP * index
                      for index in range(count + 1)]
            if abs(delta) - count * DESTRUCTIBLE_POSE_MAX_ANGLE_STEP > 1.e-9:
                angles.append(support_body[0] + delta)
            preceding = source if chassis is not None else None
            if chassis is not None:
                preceding = self._path_support(support_frame, source, proposal['flat_body'][0],
                    proposal['pivot_offset'], peers, cap, now, deadline, hydraulic, chassis, receipts)
            else:
                receipts = []
                for first, last in zip(angles, angles[1:]):
                    receipt = self._slice(support_frame, source, first, last, proposal['pivot_offset'],
                                          peers, cap, now, deadline, hydraulic)
                    receipts.append(receipt)
            if (preceding is not None and
                    (not _same_point(preceding['position'], proposal['projected_frame']['position'],
                                     _POSITION_EPSILON) or
                     not _same_point((preceding['pitch'], preceding['roll']),
                                     proposal['flat_body'][1:], NATIVE_ANGLE_TOLERANCE))):
                raise _Deferred('stationary_chassis_endpoint_disagrees')
            hydraulic_receipt = None
            if hydraulic is not None:
                self._budget(now, deadline)
                endpoint = proposal['projected_frame']['position']
                hydraulic_receipt = self._hydraulic_sweep(planned, endpoint, proposal['flat_body'],
                    hydraulic['correction'], endpoint, proposal['flat_body'],
                    proposal['hydraulic_pitch'], hydraulic)
            # A projected negative can only join the global domain after
            # every arc chunk and every native support observation finished.
            if self._dependencies(frame)[0] != dependencies:
                raise _Deferred('stationary_observations_changed')
            proof = dict(proved=True, kind='native_stationary_point_plan',
                dependencies=dependencies, source_pose=dependencies[1],
                source_support=source, pivot=dict(pivot), pivot_offset=proposal['pivot_offset'],
                arc=tuple(receipts), support_resolution=DESTRUCTIBLE_POSE_MAX_ANGLE_STEP * .5,
                projected_position=proposal['projected_frame']['position'],
                projected_body=proposal['projected_frame']['body'],
                hydraulic=hydraulic_receipt, fire_permission=False)
            if combat_detail_enabled():
                self._diagnostic_sequence = getattr(self, '_diagnostic_sequence', 0) + 1
                proof['diagnostic'] = dict(plan_id=self._diagnostic_sequence,
                    planner=id(self), epoch=self._epoch_serial, built_at=float(now),
                    producer_key=diagnostic_key, shell_index=shell['index'],
                    gun=shell.get('gun_identity'), shell=shell.get('shell_identity'),
                    target=target['key'], sample_point=tuple(raw_prediction['sample_point']),
                    source_position=frame['position'], source_body=frame['body'],
                    projected_position=proof['projected_position'],
                    projected_body=proof['projected_body'])
            result = dict(proposal, status='proved', proved=True, proof=proof,
                          reason='native_stationary_point_plan', progressing=False)
            self._plans[key] = result
            if chassis is not None and combat_detail_enabled():
                combat_detail(self.runtime, 'stationary_chassis_rotation',
                    self.runtime.actor_id, now, ('proved', target['key']),
                    lambda: dict(target=target['key'], from_yaw=support_body[0],
                        to_yaw=proposal['flat_body'][0], start=source['position'],
                        endpoint=proof['projected_position'], slices=len(receipts),
                        plan=proof.get('diagnostic')))
            return result
        except _Deferred as error:
            result = _pending(error.reason, error.progressing)
            result['progress_token'] = (self._epoch_serial, len(self._supports),
                                        len(self._arcs), len(self._plans))
            # This prefix belongs to this exact target/point call. Counts of
            # global cached supports/arcs may include work for another tank.
            # Only complete support + collision + hydraulic slices qualify.
            result['verified_arcs'] = len(receipts)
            if diagnostic_key is not None and combat_detail_enabled():
                result['diagnostic'] = dict(producer_key=diagnostic_key,
                    shell_index=shell['index'], gun=shell.get('gun_identity'),
                    shell=shell.get('shell_identity'), target=target['key'],
                    sample_point=tuple(raw_prediction['sample_point']),
                    epoch=self._epoch_serial, pending=error.reason,
                    verified_arcs=len(receipts), guard=getattr(error, 'diagnostic', None))
                trace_plan_use(self.runtime, 'plan_pending',
                    dict(key=diagnostic_key, stationary_diagnostic=result['diagnostic']),
                    now, error.reason)
            return result
        except (AttributeError, TypeError, ValueError, KeyError, IndexError,
                RuntimeError, OverflowError, ZeroDivisionError) as error:
            if combat_detail_enabled():
                runtime = self.runtime
                combat_detail(runtime, 'stationary_projection', runtime.actor_id, now,
                    type(error).__name__, lambda: dict(shell=shell['index'], target=target['key'],
                        channel=channel, error=str(error)[:200]))
            return _pending('stationary_native_projection_unavailable')
        finally:
            if costs is not None:
                costs['total_ms'] = (self.clock()-started)*1000.
                if costs['total_ms'] > 0.:
                    combat_detail(self.runtime, 'stationary_work_cost', self.runtime.actor_id,
                        now, channel, lambda: dict(costs=costs, target=target.get('key'),
                            cached_supports=len(self._supports), cached_arcs=len(self._arcs),
                            cached_plans=len(self._plans), checked_prefix=len(receipts)))

    def current(self, frame, proof):
        if isinstance(proof, dict) and isinstance(proof.get('proof'), dict):
            proof = proof['proof']
        if (not isinstance(proof, dict) or proof.get('proved') is not True or
                proof.get('kind') != 'native_stationary_point_plan'):
            return False
        current, error_text, guard = None, None, None
        try:
            current = self._dependencies(frame)[0]
            valid = proof['dependencies'] == current
            reason = 'current' if valid else 'dependencies_changed'
        except _Deferred as error:
            valid, reason = False, error.reason
            guard = getattr(error, 'diagnostic', None)
        except (AttributeError, TypeError, ValueError, KeyError, IndexError,
                RuntimeError, OverflowError, ZeroDivisionError) as error:
            valid, reason = False, 'contract_' + type(error).__name__
            error_text = str(error)[:200]
        diagnostic = proof.get('diagnostic')
        if isinstance(diagnostic, dict) and combat_detail_enabled():
            before = proof.get('dependencies') or ()
            changes = dict((name, dict(before=old, after=new)) for name, old, new in
                zip(_DEPENDENCY_NAMES, before, current) if old != new) if current is not None else {}
            diagnostic['last_check'] = dict(at=self.runtime.now, valid=bool(valid),
                reason=reason, fields=tuple(sorted(changes)))
            trace_plan_use(self.runtime, 'plan_current',
                dict(key=diagnostic.get('producer_key'), stationary_plan=dict(proof=proof)),
                self.runtime.now, (reason, tuple(sorted(changes))),
                valid=bool(valid), changes=changes, error=error_text, guard=guard)
        return valid
