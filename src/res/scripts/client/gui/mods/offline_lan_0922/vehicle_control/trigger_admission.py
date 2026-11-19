"""One shared tactical admission per new physical trigger.

This owner has no burst-tail state, cancellation, timeout or continuation API.
It proves the first launch against the observed native gun/target and retains
one random draw while that uncommitted launch is being proved. The physical
gun owns all subsequent shells, irrespective of target or controller changes.
"""
from __future__ import division

import math
import random

from .. import ballistics, combat_rules, projectile_runtime, shot_geometry
from ..projectile_wire import round_scalar
from .attack_policy import (_distance_sq, _mechanical,
                            _point, native_source_pose, native_target_pose,
                            native_geometry_complete, native_lane_geometry_complete,
                            native_chord_candidates, native_hostile_roster)
from .actor_observation import observation
from ..native_input_diagnostics import combat_detail, combat_detail_enabled


WORLD_CHORDS_PER_ATTEMPT = 24
MAX_PROOF_CHORDS = 334
NEAR_WORLD_DISTANCE = 25.
PROBE_INTERVAL = .05
FULL_PROOF_INTERVAL = .5
COMPLETED_PROOF_TTL = .2


def barrel_path(origin, direction, shot, point):
    """Sample the current real barrel to the selected target's aiming plane."""
    speed, gravity = float(shot['speed']), abs(float(shot['gravity']))
    horizontal = direction[0] ** 2 + direction[2] ** 2
    if speed <= 0. or horizontal <= 1.e-8:
        return (), (), None
    flight = sum((point[index] - origin[index]) * direction[index]
                 for index in (0, 2)) / (speed * horizontal)
    if not 0. < flight <= ballistics.PROJECTILE_MAX_FLIGHT_SECONDS:
        return (), (), None
    if speed * flight > float(shot['maxDistance']) + 1.e-6:
        return (), (), None
    yaw = math.atan2(direction[0], direction[2])
    pitch = math.atan2(-direction[1], math.sqrt(horizontal))
    path = ballistics.ballistic_path(origin, yaw, pitch, speed, gravity, flight)
    times = tuple(flight * index / (len(path) - 1) for index in range(len(path)))
    return path, times, flight


class _ScatterDraw(object):
    """Replay the same random inputs through the unchanged gun sampler."""

    def __init__(self):
        self.normal = random.gauss(0., 1.)
        self.uniforms = []
        self.cursor = 0

    def gauss(self, mean, sigma):
        return mean + sigma * self.normal

    def uniform(self, low, high):
        if self.cursor == len(self.uniforms):
            self.uniforms.append(random.uniform(0., 1.))
        value = self.uniforms[self.cursor]
        self.cursor += 1
        return low + (high - low) * value

    def scatter(self, owner, gun, direction, perfect, dispersion):
        self.cursor = 0
        result = owner._vector(direction)
        result.normalise()
        gun.scatter(result, perfect, gauss=self.gauss, uniform=self.uniform,
                    dispersion_angle=dispersion)
        return _point(result)


class TriggerAdmission(object):

    def __init__(self, control):
        self.control = control
        self.owner = control.owner
        self.physical = observation(control.runtime)
        self.reset()

    def reset(self):
        self.pending = None
        self.receipt = dict(status='idle', reason='idle')
        self._next_probe = float('-inf')
        self._next_full_probe = float('-inf')

    @staticmethod
    def terminal_reason(reason):
        return reason in ('auto_not_owned', 'auto_target_lost',
                          'auto_owner_changed', 'auto_shell_changed',
                          'auto_tail_not_admissible')

    def _result(self, status, reason, token=None, **fields):
        result = dict(status=status, reason=reason, token=token)
        result.update(fields)
        self.receipt = dict((key, value) for key, value in result.items()
                            if key not in ('token', 'target', 'path', 'raw_ray'))
        return result

    def _record_actual_refusal(self, proof, now, reason=None, blocker=None, lane_stage=None):
        if not combat_detail_enabled():
            return
        reason = reason or proof.get('refusal')
        if reason not in ('auto_front_vehicle', 'auto_world_blocked', 'auto_friendly_lane',
                          'auto_friendly_splash', 'auto_lane_geometry_unknown'):
            return
        runtime = self.control.runtime
        candidate, solution = proof.get('candidate') or {}, proof['solution']
        world = reason == 'auto_world_blocked'
        path = (proof.get('centre_path', proof['raw_path']) if lane_stage == 'centre' else
                proof['path'] if lane_stage == 'scatter' else
                proof['raw_path'] if proof['stage'] == 0 else proof['path'])
        stage = ('actual_world_refusal' if world else
                 'actual_lane_refusal' if lane_stage else 'actual_barrel_refusal')
        combat_detail(runtime, stage,
            runtime.actor_id, now,
            (reason, candidate.get('key'), lane_stage), lambda: dict(refusal=reason,
                candidate=candidate.get('key'), mode=candidate.get('mode'),
                aim_point=solution['point'], source_pose=solution.get('source_pose'),
                barrel_origin=proof['raw_ray'][0], barrel_direction=proof['raw_ray'][1],
                centre_endpoint=proof['raw_path'][-1],
                target_engine=proof['target'].id,
                contact=proof.get('centre_observation'), cursor=proof['cursor'],
                blocker=proof.get('blocker') if lane_stage is None else blocker,
                lane_stage=lane_stage, lane_path=path if lane_stage else None,
                blocked_chord=path[proof['cursor']:proof['cursor'] + 2]
                    if world and lane_stage is None else None))

    def _target(self, context):
        value = context.get('target')
        runtime = self.control.runtime
        target = runtime.target_entity(value) if isinstance(value, dict) else self.owner._server_entity(value)
        if target is None or not getattr(target, 'isStarted', False) or not target.isAlive():
            return None
        bot = getattr(runtime, 'actor_kind', 'human') == 'bot'
        if bot:
            # The hidden worker can render both teams. Rendering by its
            # observer avatar is not a spotting receipt for this BOT.
            visible = any(runtime.target_entity(row) is target
                          for row in runtime.visible_targets()
                          if row.get('alive', True) and row.get('visible', True))
            if not visible:
                return None
        for record in self.owner._records.values():
            if record.get('engine_id') != target.id:
                continue
            if (record.get('ready') and not record.get('tombstone') and
                    not self.physical.owns_record(record) and (bot or record.get('spot_visible')) and
                    int((record.get('state') or {}).get('team', 0)) != self.physical.actor_team):
                return target
        return None

    def _scene(self):
        owner = self.owner
        sensor = getattr(owner, '_destructibles', None)
        revision = getattr(sensor, '_spatial_revision_1513', None)
        return (id(owner._avatar), owner._avatar.spaceID, owner._generation,
                id(sensor), revision() if callable(revision) else None)

    def _fresh(self, context, entity, gun, raw_ray, shot, now):
        control, owner = self.control, self.owner
        if (not context.get('automatic') or not control.active or control.closed or
                control.control_generation != context.get('generation') or
                not self.physical.control_current(control)):
            return 'auto_owner_changed', None, None
        if gun is not control.runtime.gun or gun.shot_index != context.get('shell_index', gun.shot_index):
            return 'auto_shell_changed', None, None
        target = self._target(context)
        if target is None:
            return 'auto_target_lost', None, None
        solution = context.get('solution')
        if not isinstance(solution, dict):
            return 'auto_solution_unavailable', target, None
        solution = dict(solution)
        solution['point'] = _point(solution.get('point', solution.get('aim_position')))
        solution['velocity'] = _point(solution.get('velocity', (0., 0., 0.)))
        signature = native_target_pose(owner, target)[0]
        candidate = context.get('candidate')
        descriptor = self.physical.source_descriptor()
        artillery = 'SPG' in (descriptor.type.tags or ())
        if not artillery:
            if not isinstance(candidate, dict) or candidate.get('shell_index') != gun.shot_index:
                return 'auto_candidate_unavailable', target, solution
            if candidate.get('mode') == 'he_fallback':
                if (not combat_rules.is_he(shot) or candidate.get('contact') is not True or
                        candidate.get('expected_damage') is None):
                    return 'auto_he_contact_unknown', target, solution
            elif candidate.get('armor') != 'passed':
                return 'auto_penetration_unproved', target, solution
        reach = _mechanical(descriptor, raw_ray[1],
                            native_source_pose(control.runtime, raw_ray[0])[1])
        if reach['status'] != 'reachable':
            return 'auto_gun_laying', target, solution
        path, times, flight = barrel_path(raw_ray[0], raw_ray[1], shot, solution['point'])
        if not path:
            return 'auto_actual_barrel_unavailable', target, solution
        # A point inside a broad target bbox is not sufficient; the centre
        # flight must reach this selected point before its exact plate proof.
        if _distance_sq(path[-1], solution['point']) > .30 ** 2:
            return 'auto_gun_laying', target, solution
        solution.update(raw_path=path, raw_times=times, flight_time=flight,
                        target_pose=signature, artillery=artillery)
        return None, target, solution

    def _collision_roster(self, target, velocity, now):
        return native_hostile_roster(self.control.runtime, now, target, velocity)

    @staticmethod
    def _blocking_signature(roster, target, paths):
        """Only actors intersecting this shot can revoke an obstruction proof.

        Selected-target animation is not an obstacle or another armour gate.
        New or moving intervening actors still invalidate geometric work.
        """
        relevant = set()
        others = tuple(row for row in roster if row['target'] is not target)
        for path, times in paths:
            for index in range(len(path) - 1):
                for unused, row, start, end, length in native_chord_candidates(
                        others, path[index], path[index + 1], times[index], times[index + 1]):
                    relevant.add(id(row['target']))
        return tuple(row['signature'] for row in others if id(row['target']) in relevant)

    def _contact(self, proof, first, last, first_time, last_time, centre=False):
        """Find geometric obstruction without another armour/damage decision."""
        from ..entities.remote_vehicle import collide_vehicle_at_matrix
        owner, best = self.owner, None
        candidates = native_chord_candidates(proof['roster'], first, last, first_time, last_time)
        for broad_fraction, row, start, end, length in candidates:
            if best is not None and broad_fraction > best['fraction']:
                break
            proof['target_queries'] += 1
            hits = collide_vehicle_at_matrix(row['target'], row['body'],
                owner._vector(start), owner._vector(end), owner._runtime.math,
                chassis_matrix=row['chassis'])
            if not hits:
                continue
            entry_distance = min(float(hit.dist) for hit in hits)
            trace_end = combat_rules.vehicle_material_trace_end(proof['shot'], entry_distance)
            material_end = end
            if trace_end > length + 1.e-6 and not combat_rules.is_he(proof['shot']):
                material_end = tuple(start[index] + (end[index] - start[index]) * trace_end / length
                                     for index in range(3))
                proof['target_queries'] += 1
                extended = collide_vehicle_at_matrix(row['target'], row['body'],
                    owner._vector(start), owner._vector(material_end), owner._runtime.math,
                    chassis_matrix=row['chassis'])
                if extended:
                    hits = extended
            retained = combat_rules.vehicle_material_hits(hits, trace_end)
            fraction = entry_distance / length
            if not 0. <= fraction <= 1.:
                raise ValueError('native entry lies outside its queried chord')
            point = tuple(first[index] + fraction * (last[index] - first[index]) for index in range(3))
            structural = any(float(getattr(hit.matInfo, 'vehicleDamageFactor')) > 0.
                             for hit in retained)
            if not centre and not structural and not combat_rules.is_he(proof['shot']):
                # External-only geometry cannot certify that a solid shell
                # stops before a friendly vehicle. Actual material traversal
                # and all penetration rolls belong to the launched projectile.
                continue
            item = dict(fraction=fraction, point=point, row=row,
                        start=owner._vector(start), end=owner._vector(material_end),
                        hits=hits)
            if best is None or fraction < best['fraction']:
                best = item
        return best

    def _centre_verdict(self, proof, contact):
        if contact['row']['target'] is not proof['target']:
            return 'auto_front_vehicle'
        return None

    def _probe(self, first, last):
        hit = self.owner._runtime.bigworld.wg_collideSegment(
            self.owner._avatar.spaceID, self.owner._vector(first), self.owner._vector(last), 128)
        return None if hit is None else _point(hit[0])

    def _advance(self, proof, budget):
        used = 0
        while used < budget and not proof['done'] and proof.get('refusal') is None:
            centre = proof['stage'] == 0
            path = proof['raw_path'] if centre else proof['path']
            times = proof['raw_times'] if centre else proof['times']
            index = proof['cursor']
            if index >= len(path) - 1:
                if centre:
                    # Alignment is already proved. A naturally missed armour
                    # surface is a real shot outcome, not a rescan request.
                    proof['stage'], proof['cursor'] = 1, 0
                    continue
                else:
                    proof['done'] = True
                break
            first, last = path[index], path[index + 1]
            hit = self._probe(first, last)
            used += 1
            target = self._contact(proof, first, last, times[index], times[index + 1], centre)
            fraction = None
            if hit is not None:
                delta = tuple(last[axis] - first[axis] for axis in range(3))
                length2 = sum(value * value for value in delta)
                fraction = (sum((hit[axis] - first[axis]) * delta[axis] for axis in range(3)) / length2
                            if length2 > 0. else -1.)
                closest = tuple(first[axis] + fraction * delta[axis] for axis in range(3))
                if not -.0001 <= fraction <= 1.0001 or _distance_sq(closest, hit) > .1 ** 2:
                    proof['refusal'] = 'auto_world_geometry_unknown'
                    break
            if target is not None and (hit is None or target['fraction'] <= fraction):
                if centre:
                    proof['centre_path'] = tuple(path[:index + 1]) + (target['point'],)
                    proof['refusal'] = self._centre_verdict(proof, target)
                    if combat_detail_enabled():
                        proof['centre_observation'] = dict(actor=target['row']['actor_key'],
                            point=target['point'], geometry_only=True)
                    if proof['refusal'] == 'auto_front_vehicle':
                        row = target['row']
                        # Native entity ids and tactical actor ids are not
                        # interchangeable. Keep the actual first collision so
                        # the same admitted enemy domain can review it; this
                        # receipt neither selects it nor permits a shot.
                        proof['blocker'] = dict(kind='vehicle', point=target['point'],
                            vehicle_id=row['target'].id, actor_key=row['actor_key'],
                            team=row['team'], hostile=(
                                row['team'] != self.physical.actor_team
                                if row['team'] in (1, 2) else None),
                            target_pose=row['signature'][1])
                    proof['stage'], proof['cursor'] = 1, 0
                    continue
                proof['path'] = tuple(path[:index + 1]) + (target['point'],)
                proof['terminal_impact'] = target['point']
                proof['terminal_kind'] = 'vehicle'
                proof['terminal_vehicle'] = target['row']['target'].id
                proof['done'] = True
                break
            if hit is not None:
                if centre or _distance_sq(hit, path[0]) <= NEAR_WORLD_DISTANCE ** 2:
                    proof['refusal'] = 'auto_world_blocked'
                    # A scattered obstruction affects this shot trajectory,
                    # independently of the selected point's centre ray.
                    proof['blocker'] = dict(kind='world', point=hit,
                                            ray_stage='centre' if centre else 'scatter')
                    break
                proof['path'] = tuple(path[:index + 1]) + (hit,)
                proof['terminal_impact'] = hit
                proof['terminal_kind'] = 'world'
                proof['done'] = True
                break
            proof['cursor'] += 1
        if proof['stage'] == 1 and proof['cursor'] >= len(proof['path']) - 1:
            proof['done'] = True
        return used

    def _lane(self, path, splash=0.):
        runtime = self.control.runtime
        if not native_lane_geometry_complete(runtime):
            return 'auto_lane_geometry_unknown', dict(reason='attached_collision_unavailable')
        verdict = runtime.geometry._bot_friendly_path_verdict(runtime.current_source(), path, splash)
        if isinstance(verdict, dict) and verdict.get('clear') is True:
            return None, None
        if (isinstance(verdict, dict) and verdict.get('blocked') is True and
                verdict.get('blocker_kind') in ('wreck', 'debris')):
            return 'auto_world_blocked', verdict
        if isinstance(verdict, dict) and verdict.get('blocker_team') is not None:
            return 'auto_friendly_lane' if splash <= 0. else 'auto_friendly_splash', verdict
        return 'auto_lane_geometry_unknown', verdict

    def _dynamic(self, proof):
        reason, blocker = self._lane(proof.get('centre_path', proof['raw_path']))
        if reason is not None:
            self._record_actual_refusal(proof, self.control.runtime.now, reason, blocker, 'centre')
            return reason, blocker
        splash = combat_rules.he_radius(proof['shot']) if proof.get('terminal_impact') is not None else 0.
        reason, blocker = self._lane(proof['path'], splash)
        if reason is not None:
            self._record_actual_refusal(proof, self.control.runtime.now, reason, blocker, 'scatter')
        return reason, blocker

    @staticmethod
    def _launch_path(origin, velocity, gravity, maximum, near_limit=None, flight_limit=None):
        try:
            origin, velocity = _point(origin), _point(velocity)
            gravity, maximum = float(gravity), float(maximum)
            if (sum(value * value for value in velocity) <= 1.e-12 or
                    maximum <= 0. or gravity < 0. or
                    any(math.isnan(value) or math.isinf(value) for value in (gravity, maximum))):
                return (), ()
        except (TypeError, ValueError, IndexError, KeyError):
            return (), ()
        limit = (ballistics.PROJECTILE_MAX_FLIGHT_SECONDS if flight_limit is None else
                 min(ballistics.PROJECTILE_MAX_FLIGHT_SECONDS, flight_limit))
        path, times, travelled = [origin], [0.], 0.
        count = int(math.ceil(limit / .12))
        for index in range(1, count + 1):
            end = min(limit, index * .12)
            first, last, actual, terminal = projectile_runtime.prepare_chord(
                origin, velocity, (0., -gravity, 0.), 0., times[-1], end, maximum, travelled)
            travelled += math.sqrt(_distance_sq(first, last))
            path.append(_point(last))
            times.append(actual)
            if terminal or near_limit is not None and _distance_sq(origin, last) > near_limit ** 2:
                break
        return tuple(path), tuple(times)

    def _centre_path(self, raw_ray, shot, solution, target, roster):
        """Prove through the observed target, not merely to an interior sample.

        A component's aiming sample can be in empty space before its BSP.
        Horizontal relative motion bounds the last possible contact with the
        entire native envelope; vertical motion, plates, intervening vehicles
        and world geometry still require the normal chord proofs.
        """
        row = next((item for item in roster if item['target'] is target), None)
        if row is None:
            return (), ()
        origin, direction = raw_ray
        length = math.sqrt(sum(value * value for value in direction))
        velocity = tuple(value * float(shot['speed']) / length for value in direction)
        enter, leave = 0., ballistics.PROJECTILE_MAX_FLIGHT_SECONDS
        for axis in (0, 2):
            low, high = row['bounds'][0][axis], row['bounds'][1][axis]
            relative = velocity[axis] - row['velocity'][axis]
            if relative == 0.:
                if not low <= origin[axis] <= high:
                    return solution['raw_path'], solution['raw_times']
                continue
            first, last = (low - origin[axis]) / relative, (high - origin[axis]) / relative
            enter, leave = max(enter, min(first, last)), min(leave, max(first, last))
            if leave < enter:
                return solution['raw_path'], solution['raw_times']
        return self._launch_path(origin, velocity, abs(float(shot['gravity'])),
            float(shot['maxDistance']), flight_limit=max(solution['flight_time'], leave))

    def _shot_draw(self, gun):
        key = (self.owner._generation, self.control.control_generation,
               id(gun), gun.shot_index, tuple(gun.ammo), gun.clip)
        if self.pending is None or self.pending['weapon_key'] != key:
            self.pending = dict(weapon_key=key, draw=_ScatterDraw(), proof=None,
                restarts=0, penetration_factor=round_scalar(combat_rules.sample_penetration_factor()))
        return self.pending

    def _scattered_velocity(self, token, gun, direction, dispersion, shot):
        perfect = bool(getattr(self.control.runtime, 'actor_kind', 'human') == 'human' and
                       self.owner._config and self.owner._config.get('perfect_accuracy', False))
        direction = token['draw'].scatter(self.owner, gun, direction, perfect, dispersion)
        return perfect, tuple(round_scalar(value * float(shot['speed'])) for value in direction)

    def recheck_world_scatter(self, row, now):
        """Re-observe a refused point without laying the gun or issuing a trigger."""
        try:
            gun = self.control.runtime.gun
            if gun.shot_index != row['shell_index'] or self.physical.trigger_active():
                return None
            solution = row['solution']
            shot = self.physical.source_shot(gun.shot_index)
            target = self._target(dict(target=row['target']))
            dispersion = self.physical.native_dispersion_angle()
            if target is None or dispersion is None:
                return None
            origin, direction = solution['origin'], solution['direction']
            # Use the exact observed muzzle when it is already laid at this
            # point. Otherwise review the current intended ray with the same
            # sampled dispersion, leaving the final proof to admission.
            actual = self.physical.mutable_shot_ray()
            if actual and _distance_sq(_point(actual[1]), direction) <= 1.e-10:
                origin, direction = _point(actual[0]), _point(actual[1])
            origin = tuple(round_scalar(value) for value in origin)
            token = self._shot_draw(gun)
            unused, velocity = self._scattered_velocity(token, gun, direction, dispersion, shot)
            path, times = self._launch_path(origin, velocity, round_scalar(float(shot['gravity'])),
                round_scalar(float(shot['maxDistance'])), near_limit=NEAR_WORLD_DISTANCE)
            if len(path) < 2 or len(path) > WORLD_CHORDS_PER_ATTEMPT + 1:
                return None
            roster = self._collision_roster(target, solution['velocity'], now)
            if roster is None:
                return None
            scene = self._scene()
            proof = dict(path=path, times=times, cursor=0, stage=1, done=False,
                         refusal=None, roster=roster, target_queries=0, shot=shot)
            self._advance(proof, WORLD_CHORDS_PER_ATTEMPT)
            if token is self.pending and self._scene() == scene:
                return proof['done'] and proof['refusal'] is None
        except (AttributeError, TypeError, ValueError, KeyError, IndexError,
                RuntimeError, OverflowError, ZeroDivisionError) as error:
            if combat_detail_enabled():
                runtime = self.control.runtime
                combat_detail(runtime, 'scatter_recheck_unavailable', runtime.actor_id, now,
                    type(error).__name__, lambda: dict(candidate=row.get('key'),
                        error_type=type(error).__name__, error=str(error)[:200]))
        return None

    def _feedback(self, context, reason, blocker=None):
        policy = getattr(self.control.runtime, 'attack_policy', None)
        if policy is not None:
            policy.admission_failed(context.get('candidate'), reason, blocker)

    def prepare(self, context, entity, gun, raw_ray, dispersion, source_shot,
                now, range_origin=None, artillery_launch=None):
        if not context.get('automatic'):
            return self._result('rejected', 'auto_not_owned')
        if self.physical.trigger_active():
            return self._result('rejected', 'auto_tail_not_admissible')
        try:
            now = float(now)
            raw_ray = (_point(raw_ray[0]), _point(raw_ray[1]))
            reason, target, solution = self._fresh(context, entity, gun, raw_ray, source_shot, now)
            if reason is not None:
                if self.terminal_reason(reason):
                    self.pending = None
                self._feedback(context, reason)
                return self._result('rejected' if self.terminal_reason(reason) else 'pending', reason)
            candidate = self._shot_draw(gun)
            roster = self._collision_roster(target, solution['velocity'], now)
            if roster is None:
                return self._result('pending', 'auto_collision_geometry_unknown')
            if artillery_launch is not None and solution['artillery']:
                # The worker has already proved this dispersed artillery arc.
                # Review the same launch that its physical gun will commit.
                perfect = False
                origin = tuple(round_scalar(value) for value in artillery_launch['origin'])
                velocity = tuple(round_scalar(value) for value in artillery_launch['velocity'])
            else:
                perfect, velocity = self._scattered_velocity(
                    candidate, gun, raw_ray[1], dispersion, source_shot)
                origin = tuple(round_scalar(value) for value in raw_ray[0])
            gravity = round_scalar(float(source_shot['gravity']))
            maximum = round_scalar(float(source_shot['maxDistance']))
            range_origin = tuple(round_scalar(value) for value in (
                self.physical.source_pose()[0] if range_origin is None else range_origin))
            # Bound actor changes to the current firing lane. The world and
            # friendly probes below retain their own current geometry checks.
            roster_signature = self._blocking_signature(roster, target,
                ((solution['raw_path'], solution['raw_times']),))
            geometry = (raw_ray, float(dispersion), perfect, solution['point'],
                        roster_signature,
                        range_origin, velocity, gravity, maximum,
                        (context.get('candidate') or {}).get('mode'), id(target))
            scene = self._scene()
            proof = candidate['proof']
            if (proof is None or proof['geometry'] != geometry or proof['scene'] != scene or
                    proof.get('refusal') is not None or
                    proof['done'] and now - proof['completed'] > COMPLETED_PROOF_TTL):
                if proof is not None and (proof['cursor'] or proof['stage']):
                    candidate['restarts'] += 1
                path, times = self._launch_path(origin, velocity, gravity, maximum)
                raw_path, raw_times = self._centre_path(raw_ray, source_shot, solution, target, roster)
                if len(path) < 2 or len(raw_path) < 2:
                    return self._result('pending', 'auto_actual_barrel_unavailable')
                if len(path) + len(raw_path) - 2 > MAX_PROOF_CHORDS:
                    return self._result('pending', 'auto_path_budget_exceeded')
                proof = dict(geometry=geometry, raw_ray=raw_ray,
                    raw_path=raw_path, raw_times=raw_times,
                    path=path, times=times, origin=origin, velocity=velocity,
                    gravity=gravity, maximum=maximum, range_origin=range_origin,
                    stage=0, cursor=0, done=False, refusal=None, completed=None,
                    created=now, scene=scene, target=target, solution=solution,
                    candidate=context.get('candidate'), roster=roster,
                    roster_signature=roster_signature, target_queries=0,
                    shot=source_shot, penetration_factor=candidate['penetration_factor'])
                candidate['proof'] = proof
            full = candidate['restarts'] >= 2
            used = 0
            if not proof['done']:
                if now < self._next_probe or full and now < self._next_full_probe:
                    return self._result('pending', 'auto_proof_pending', candidate, world_chords=0)
                self._next_probe = now + PROBE_INTERVAL
                if full:
                    self._next_full_probe = now + FULL_PROOF_INTERVAL
                used = self._advance(proof, MAX_PROOF_CHORDS if full else WORLD_CHORDS_PER_ATTEMPT)
                if candidate is not self.pending or self._scene() != scene:
                    candidate['proof'] = None
                    return self._result('pending', 'auto_world_changed', world_chords=used)
                if proof.get('refusal') is not None:
                    self._record_actual_refusal(proof, now)
                    self._feedback(context, proof['refusal'], proof.get('blocker'))
                    return self._result('pending', proof['refusal'], candidate, world_chords=used,
                                        blocker=proof.get('blocker'))
                if not proof['done']:
                    return self._result('pending', 'auto_proof_pending', candidate, world_chords=used)
                proof['completed'] = float(self.owner._clock())
                proof['blocking_signature'] = self._blocking_signature(roster, target,
                    ((proof.get('centre_path', proof['raw_path']), proof['raw_times']),
                     (proof['path'], proof['times'])))
            reason, blocker = self._dynamic(proof)
            if reason is not None:
                self._feedback(context, reason, blocker)
                return self._result('pending', reason, candidate, world_chords=used, blocker=blocker)
            candidate.update(context=context, target=target, source_shot=source_shot,
                             solution=solution, entity=entity, gun=gun)
            return self._result('ready', 'clear', candidate,
                origin=proof['origin'], velocity=proof['velocity'],
                penetration_factor=candidate['penetration_factor'],
                world_chords=used, target_queries=proof['target_queries'],
                proof_mode='complete' if full else 'sliced',
                terminal_kind=proof.get('terminal_kind'),
                terminal_vehicle=proof.get('terminal_vehicle'))
        except (AttributeError, TypeError, ValueError, KeyError, IndexError,
                RuntimeError, OverflowError, ZeroDivisionError):
            return self._result('pending', 'auto_geometry_unavailable')

    def validate(self, token, context, entity, gun, now, launch=None):
        if token is None or token is not self.pending or not token.get('proof', {}).get('done'):
            return 'auto_candidate_changed'
        proof = token['proof']
        try:
            now = float(self.owner._clock())
            if (self._scene() != proof['scene'] or
                    not 0. <= now - proof['completed'] <= COMPLETED_PROOF_TTL):
                token['proof'] = None
                return 'auto_world_changed'
            native = self.physical.mutable_shot_ray()
            raw_ray = (_point(native[0]), _point(native[1]))
            if (raw_ray != proof['raw_ray'] or
                    self.physical.native_dispersion_angle() != proof['geometry'][1]):
                token['proof'] = None
                return 'auto_pose_changed'
            reason, target, solution = self._fresh(context, entity, gun, raw_ray,
                                                   token['source_shot'], now)
            if reason is not None:
                return reason
            roster = self._collision_roster(target, solution['velocity'], now)
            if (target is not token['target'] or entity is not token['entity'] or gun is not token['gun'] or
                    tuple(gun.ammo) != token['weapon_key'][4] or gun.clip != token['weapon_key'][5] or
                    solution['point'] != token['solution']['point'] or roster is None):
                token['proof'] = None
                return 'auto_target_changed'
            paths = ((proof.get('centre_path', proof['raw_path']), proof['raw_times']),
                     (proof['path'], proof['times']))
            if self._blocking_signature(roster, target, paths) != proof['blocking_signature']:
                token['proof'] = None
                return 'auto_obstruction_changed'
            if launch is not None and (
                    tuple(launch['origin']) != proof['origin'] or
                    tuple(launch['velocity']) != proof['velocity'] or
                    launch['gravity'] != proof['gravity'] or
                    launch['max_distance'] != proof['maximum'] or
                    tuple(launch['range_origin']) != proof['range_origin'] or
                    launch['penetration_factor'] != proof['penetration_factor']):
                return 'auto_launch_changed'
            reason, blocker = self._dynamic(proof)
            if reason is not None:
                self._feedback(context, reason, blocker)
                return reason
            # Friendly/native component probes can re-enter game callbacks.
            # Fence the frozen launch and relevant obstruction observations
            # after native probes, without repeating tactical armour checks.
            latest = self.physical.mutable_shot_ray()
            if ((_point(latest[0]), _point(latest[1])) != proof['raw_ray'] or
                    self.physical.native_dispersion_angle() != proof['geometry'][1] or
                    not 0. <= float(self.owner._clock()) - proof['completed'] <= COMPLETED_PROOF_TTL):
                token['proof'] = None
                return 'auto_pose_changed'
            final_roster = self._collision_roster(target, solution['velocity'], now)
            if (final_roster is None or
                    self._blocking_signature(final_roster, target, paths) != proof['blocking_signature']):
                token['proof'] = None
                return 'auto_obstruction_changed'
            if (token is not self.pending or self._scene() != proof['scene'] or
                    not self.control.active or self.control.closed or
                    self.control.control_generation != context.get('generation') or
                    not self.physical.control_current(self.control)):
                return 'auto_owner_changed'
            return None
        except (AttributeError, TypeError, ValueError, KeyError, IndexError,
                RuntimeError, OverflowError, ZeroDivisionError):
            return 'auto_geometry_unavailable'

    def deferred(self, reason):
        self.receipt.update(status='pending', reason=reason)

    def rejected(self, reason):
        self.pending = None
        self.receipt.update(status='rejected', reason=reason)

    def committed(self, token):
        if self.pending is token:
            self.pending = None
        self.receipt.update(status='committed', reason='trigger_started')
