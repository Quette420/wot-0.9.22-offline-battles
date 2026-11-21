"""Active hydraulic aim/finite-TD proofs, never prospective mode admission.

Native observation fixtures feed production policy, source inversion
and hydraulic actuation. These tests do
not establish physical Windows client timing/rendering acceptance.
"""
from contextlib import redirect_stdout
from io import StringIO
import json
import math
import os
import unittest
from unittest import mock

from test_player_siege_engagement import SiegeScene
from test_player_limited_traverse import install_ground_observations
from gui.mods.offline_lan_0922 import shot_geometry, siege_mechanics, tank_collision, vehicle_physics
from gui.mods.offline_lan_0922.vehicle_control import siege_planning
from gui.mods.offline_lan_0922.vehicle_control.native_aim import (
    active_hydraulic_pose, hydraulic_body, hydraulic_reach, mechanical_reach)


class ActualHydraulicScene(SiegeScene):
    def configure_hydraulics(self, **kwargs):
        self.configure(**kwargs)
        enabled = self.entity.siegeState
        self.position = (0., 0., 0.)
        install_ground_observations(self)
        self.entity.siegeState = enabled
        self.observe()
        return self

    def evaluated_row(self, sample=0, mode='penetration'):
        policy = self.runtime.attack_policy
        self.observe()
        policy.frame = policy.evaluator.snapshot(self.now)
        job = next(job for job in policy._jobs(mode, self.runtime.gun.shot_index)
                   if job[2]['entity'] is self.target and job[3] == sample)
        return policy._evaluate(job, self.now, 'foreground')


class ActualSiegeAimTests(unittest.TestCase):
    def test_recorded_rear_ray_uses_opposite_hydraulic_edge_before_checked_turn(self):
        scene = self.scene(enabled_pitch=(-math.radians(4),math.radians(2)))
        flat = (-2.588335037,-.013411073,.157022864)
        local = (.30818735293,-.04354924457,-.95032837419)
        direction = shot_geometry.transform_vehicle_vector(local,*flat)
        config = dict(isAvailable=True,isEnabled=True,
                      minimum=-math.radians(11),maximum=math.radians(11),speed=.2)
        result = hydraulic_reach(scene.entity.typeDescriptor,direction,flat,config)
        self.assertTrue(result['needs_hull'],result)
        self.assertFalse(result['reachable'])
        self.assertLess(result['hydraulic_pitch'],0.)
        self.assertGreaterEqual(result['local_pitch'],result['pitch_limits'][0]-1.e-8)
        self.assertLessEqual(result['local_pitch'],result['pitch_limits'][1]+1.e-8)

    def scene(self, **kwargs):
        scene = ActualHydraulicScene()
        scene.setUp()
        self.addCleanup(scene.doCleanups)
        return scene.configure_hydraulics(**kwargs)

    def test_future_mode_precheck_api_is_removed(self):
        for name in ('SiegePrecheck', 'project_solution', 'PRECHECK_CANDIDATES'):
            self.assertFalse(hasattr(siege_planning, name))

    def test_owned_pivot_point_precedes_another_pending_global_sample(self):
        scene = self.scene(enabled_pitch=(0., 0.), hydraulic_center=1.5)
        first = scene.evaluated_row(sample=0)
        held = scene.evaluated_row(sample=5)
        policy, combat = scene.runtime.attack_policy, scene.runtime.combat_stop
        combat.pivot = dict(key=held['key'], candidate=held, gun=scene.runtime.gun,
                            shell=policy.frame['loaded'], target_key=held['target_key'])
        combat.receipt['selected'] = held['target_key']
        result = scene.runtime.siege_aim.candidate(policy.frame, scene.now, first)
        self.assertIsNotNone(result, scene.runtime.siege_aim.status())
        self.assertEqual(held['key'], result['key'])
        self.assertFalse(policy._executable(result))

    def test_owned_pivot_point_gets_first_bounded_refresh_after_target_moves(self):
        scene = self.scene(enabled_pitch=(0., 0.), hydraulic_center=1.5)
        first = scene.evaluated_row(sample=0)
        held = scene.evaluated_row(sample=5)
        policy, combat = scene.runtime.attack_policy, scene.runtime.combat_stop
        combat.pivot = dict(key=held['key'], candidate=held, gun=scene.runtime.gun,
                            shell=policy.frame['loaded'], target_key=held['target_key'])
        combat.receipt['selected'] = held['target_key']
        policy.selected = first['key']
        scene.fixture.now += .11
        scene.pose(scene.target, (1., 12., 100.))
        scene.observe()
        policy.frame = policy.evaluator.snapshot(scene.now)
        policy.foreground_budget = 1
        policy.atomic_time_budget = 0.
        policy._used['foreground'] = 0
        jobs = policy._jobs(shell_index=policy.frame['loaded'])
        policy.ordered_load()._inspect(policy, scene.now, jobs)
        self.assertEqual(scene.now, policy.rows[held['key']]['observed_at'])
        self.assertLess(policy.rows[first['key']]['observed_at'], scene.now)
        self.assertEqual(1, policy._used['foreground'])

    def test_current_executable_sample_precedes_the_owned_pending_pivot(self):
        scene = self.scene(enabled_pitch=(-.2, .2), hydraulic_center=1.5)
        first = scene.evaluated_row(sample=0)
        held = scene.evaluated_row(sample=5)
        policy, combat = scene.runtime.attack_policy, scene.runtime.combat_stop
        self.assertTrue(policy._executable(first))
        combat.pivot = dict(key=held['key'], candidate=held, gun=scene.runtime.gun,
                            shell=policy.frame['loaded'], target_key=held['target_key'])
        combat.receipt['selected'] = held['target_key']
        result = scene.runtime.siege_aim.candidate(policy.frame, scene.now, first)
        self.assertIsNotNone(result, scene.runtime.siege_aim.status())
        self.assertEqual(first['key'], result['key'])

    def test_disabled_mode_never_inspects_targets_or_native_sources(self):
        scene = self.scene(enabled=False)
        frame = scene.runtime.attack_policy.evaluator.snapshot(scene.now)
        with mock.patch.object(scene.battle._runtime, 'get_shot_angles') as angles:
            self.assertIsNone(scene.runtime.siege_aim.candidate(frame, scene.now))
        angles.assert_not_called()
        self.assertEqual('inactive', scene.runtime.siege_aim.status()['status'])

    def test_current_heading_pitch_refusal_logs_only_with_detailed_diagnostics(self):
        scene = self.scene(enabled_pitch=(0., 0.))
        scene.pose(scene.target, (0., 55., 100.))
        row = scene.evaluated_row()
        policy, helper = scene.runtime.attack_policy, scene.runtime.siege_aim
        row = dict(row, line='clear')
        policy.rows[row['key']] = row
        for enabled in ('0', '1'):
            output = StringIO()
            with self.subTest(enabled=enabled), mock.patch.dict(os.environ,
                    {'WOT_OFFLINE_DIAGNOSTICS': '1',
                     'WOT_OFFLINE_COMBAT_DIAGNOSTICS': enabled}), redirect_stdout(output):
                self.assertIsNone(helper.candidate(policy.frame, scene.now, row))
            self.assertEqual(0, helper.status()['native_calls'])
            records = [json.loads(line.split('BATTLE REVIEW ', 1)[1])
                       for line in output.getvalue().splitlines()
                       if 'BATTLE REVIEW ' in line and 'siege_hydraulic_reach' in line]
            self.assertEqual(int(enabled), len(records))
            if records:
                self.assertEqual('hydraulic_pitch_limit', records[0]['reach']['reason'])

    def test_actual_selected_point_is_motion_only_and_adds_no_world_armour_work(self):
        scene = self.scene(enabled_pitch=(0., 0.), hydraulic_center=1.5)
        row = scene.evaluated_row()
        policy = scene.runtime.attack_policy
        before_rows, before_world = dict(policy.rows), len(scene.world_queries)
        with mock.patch.object(policy.evaluator, 'evaluate', side_effect=AssertionError('second evaluator')):
            result = scene.runtime.siege_aim.candidate(policy.frame, scene.now, row)
        self.assertIsNotNone(result, scene.runtime.siege_aim.status())
        self.assertEqual(before_rows, policy.rows)
        self.assertEqual(before_world, len(scene.world_queries))
        self.assertTrue(result['solution']['needs_hydraulic'])
        self.assertTrue(result['solution']['siege_aim'])
        self.assertFalse(result['solution']['reachable'])
        self.assertFalse(result['solution']['source_verified'])
        self.assertFalse(policy._executable(result))
        self.assertLessEqual(scene.runtime.siege_aim.status()['native_calls'], siege_planning.NATIVE_SOURCE_CALLS)

    def test_matching_flat_input_inverts_exact_native_actuator_contract(self):
        scene = self.scene(enabled_pitch=(0., 0.), hydraulic_center=-1.5)
        row = scene.evaluated_row()
        helper = scene.runtime.siege_aim
        candidate = helper.candidate(scene.runtime.attack_policy.frame, scene.now, row)
        self.assertIsNotNone(candidate, helper.status())
        source = helper.hydraulic_point(candidate, candidate['solution']['point'])
        self.assertIsNotNone(source)
        self.assertTrue(scene.runtime.weapon.preaim(candidate))
        # Exercise the actual native sender and body-pitch consumer.
        scene.runtime._siege_aim_candidate = candidate
        scene.runtime.attack_policy.decision = dict(action='firing_position', candidate=row,
                                                     reason='native_firing_position')
        for unused in range(15):
            scene.actuate_native_source(.1)
        self.assertAlmostEqual(candidate['solution']['hydraulic_pitch'],
                               scene.battle._local_siege_aim_pitch, places=6)
        self.assertFalse(scene.battle._projectile_meta)

    def test_failed_native_inverse_attempts_are_logged_only_with_opt_in(self):
        scene = self.scene(enabled_pitch=(0., 0.))
        row = scene.evaluated_row()
        policy, helper = scene.runtime.attack_policy, scene.runtime.siege_aim
        angles = (.2, -.1)
        for enabled in ('0', '1'):
            with self.subTest(enabled=enabled):
                output = StringIO()
                with mock.patch.dict(os.environ, {'WOT_OFFLINE_DIAGNOSTICS': '1',
                        'WOT_OFFLINE_COMBAT_DIAGNOSTICS': enabled}), \
                        mock.patch.object(scene.battle._runtime, 'get_shot_angles',
                                          return_value=angles) as getter, redirect_stdout(output):
                    self.assertIsNone(helper.candidate(policy.frame, scene.now, row))
                self.assertEqual(siege_planning.NATIVE_SOURCE_CALLS, getter.call_count)
                self.assertEqual('actual_hydraulic_native_source_pending', helper.status()['reason'])
                records = [json.loads(line.split('BATTLE REVIEW ', 1)[1])
                           for line in output.getvalue().splitlines()
                           if 'BATTLE REVIEW ' in line and 'siege_hydraulic_inverse' in line]
                self.assertEqual(int(enabled), len(records))
                if records:
                    inverse = records[0]['inverse']
                    self.assertEqual('attempts_exhausted', inverse['failure'])
                    self.assertEqual(siege_planning.NATIVE_SOURCE_CALLS, len(inverse['attempts']))
                    self.assertTrue(all(entry['angles'] == list(angles)
                                        for entry in inverse['attempts']))

    def test_only_small_native_yaw_error_is_accepted_for_laying(self):
        scene = self.scene()
        runtime = scene.runtime
        frame = runtime.attack_policy.evaluator.snapshot(scene.now)
        hydraulic = active_hydraulic_pose(runtime, frame)
        shell = frame['shells'][0]
        solution = dict(point=(0., 0., 100.), direction=(0., 0., 1.), hydraulic_pitch=0.)
        for angles, expected in (((1.42e-7, 0.), solution['point']),
                                 ((1.1e-6, 0.), None),
                                 ((1.42e-7, 1.1e-6), None)):
            with self.subTest(angles=angles), mock.patch.object(
                    scene.battle._runtime, 'get_shot_angles', return_value=angles):
                self.assertEqual(expected,
                    runtime.siege_aim._motion_source(frame, hydraulic, solution, shell))

    def test_pitch_rounding_uses_best_reachable_native_input_after_strict_attempts(self):
        scene = self.scene(enabled_pitch=(-.3490658402442932, 0.))
        runtime = scene.runtime
        frame = runtime.attack_policy.evaluator.snapshot(scene.now)
        hydraulic = active_hydraulic_pose(runtime, frame)
        correction = .1296901442021811
        solution = dict(point=(0., 0., 100.), direction=(0., 0., 1.),
                        hydraulic_pitch=correction)
        # The smallest pitch/correction residual of the six Redshire calls.
        residual = 2.272338354702974e-7
        angles = [(2.57e-7, correction + error) for error in
                  (1.3e-6, 5.1e-7, 3.7e-7, 4.2e-7, residual, 4.4e-7)]
        for strict in (False, True):
            with self.subTest(strict=strict):
                trace = {}
                attempts = angles if not strict else angles[:3] + [(0., correction + 5.e-8)]
                with mock.patch.object(scene.battle._runtime, 'get_shot_angles',
                                       side_effect=attempts) as getter:
                    source = runtime.siege_aim._motion_source(
                        frame, hydraulic, solution, frame['shells'][0], trace)
                self.assertEqual(len(attempts), getter.call_count)
                self.assertEqual(trace['attempts'][3 if strict else 4]['point'], source)
                self.assertEqual(not strict, trace.get('accepted_with_pitch_tolerance', False))
                self.assertFalse(scene.launches())
        # A small error beyond hydraulic travel is still out of range.
        solution['hydraulic_pitch'] = hydraulic['maximum']
        with mock.patch.object(scene.battle._runtime, 'get_shot_angles',
                               return_value=(0., hydraulic['maximum'] + residual)):
            self.assertIsNone(runtime.siege_aim._motion_source(
                frame, hydraulic, solution, frame['shells'][0]))

    def test_source_is_revoked_on_target_motion_shell_change_or_mode_exit(self):
        for change in ('target', 'shell', 'mode'):
            with self.subTest(change=change):
                scene = self.scene()
                row = scene.evaluated_row()
                helper = scene.runtime.siege_aim
                result = helper.candidate(scene.runtime.attack_policy.frame, scene.now, row)
                self.assertIsNotNone(result, helper.status())
                if change == 'target':
                    scene.pose(scene.target, (2., 12., 100.))
                elif change == 'shell':
                    scene.runtime.gun.shot_index = 1
                else:
                    scene.entity.siegeState = siege_mechanics.DISABLED
                self.assertIsNone(helper.hydraulic_point(result, result['solution']['point']))

    def test_mismatched_raw_policy_observation_cannot_publish_a_motion_source(self):
        scene = self.scene()
        row = scene.evaluated_row()
        row = dict(row, pose_stamp=('forged',))
        helper = scene.runtime.siege_aim
        self.assertIsNone(helper.candidate(scene.runtime.attack_policy.frame, scene.now, row))
        self.assertEqual(0, helper.status()['native_calls'])

    def test_blocked_point_yields_to_another_point_and_can_recover(self):
        scene = self.scene()
        first = scene.evaluated_row(sample=0)
        other = scene.evaluated_row(sample=1)
        runtime = scene.runtime
        policy, helper = runtime.attack_policy, runtime.siege_aim
        blocked = dict(first, line='enemy_blocked')
        policy.rows[first['key']] = blocked
        candidate = helper.candidate(policy.frame, scene.now, blocked)
        self.assertIsNotNone(candidate, helper.status())
        self.assertEqual(other['key'], candidate['key'])

        policy.rows[first['key']] = first
        candidate = helper.candidate(policy.frame, scene.now, first)
        self.assertIsNotNone(candidate, helper.status())
        self.assertEqual(first['key'], candidate['key'])

    def test_target_change_during_native_inverse_revokes_motion_result(self):
        scene = self.scene()
        row = scene.evaluated_row()
        getter = scene.battle._runtime.get_shot_angles

        def changed(*args):
            result = getter(*args)
            scene.pose(scene.target, (4., 12., 100.))
            return result

        with mock.patch.object(scene.battle._runtime, 'get_shot_angles', changed):
            helper = scene.runtime.siege_aim
            self.assertIsNone(helper.candidate(scene.runtime.attack_policy.frame, scene.now, row))
        self.assertEqual('actual_hydraulic_observation_changed', helper.status()['reason'])

    def test_hydraulic_compose_is_exact_on_rolled_ground_with_nonzero_pivot(self):
        position, flat, correction, center = (1., 2., 3.), (.4, .13, -.17), -.12, 1.5
        mounted, actual = hydraulic_body(position, flat, correction, center)
        local = (.2, .8, 1.3)
        expected = shot_geometry.transform_vehicle_point(
            shot_geometry.transform_vehicle_point(local, (0., center * math.sin(correction),
                center * (1. - math.cos(correction))), 0., correction, 0.), position, *flat)
        observed = shot_geometry.transform_vehicle_point(local, mounted, *actual)
        for left, right in zip(expected, observed):
            self.assertAlmostEqual(left, right, places=10)

    def test_hydraulic_reach_uses_local_composition_not_euler_pitch_addition(self):
        scene = self.scene(enabled_pitch=(0., 0.))
        frame = scene.runtime.attack_policy.evaluator.snapshot(scene.now)
        hydraulic = active_hydraulic_pose(scene.runtime, frame)
        flat, correction = (.3, .1, .2), -.15
        unused, actual = hydraulic_body((0., 0., 0.), flat, correction, 0.)
        direction = shot_geometry.transform_vehicle_vector((0., 0., 1.), *actual)
        result = hydraulic_reach(frame['descriptor'], direction, flat, hydraulic)
        self.assertTrue(result['reachable'], result)
        self.assertAlmostEqual(correction, result['hydraulic_pitch'], places=6)
        capability = mechanical_reach(frame['descriptor'], direction, flat, dict(hydraulic, body=flat))
        self.assertTrue(capability['reachable'], capability)


class ActualHydraulicStationaryTests(unittest.TestCase):
    @staticmethod
    def complete_ground_pose(scene):
        battle, descriptor = scene.battle, scene.entity.typeDescriptor
        params = vehicle_physics.derive_suspension_params(descriptor)
        state = dict(height=0., pitch=0., roll=0., vertical_velocity=0.,
                     pitch_velocity=0., roll_velocity=0.)
        for unused in range(150):
            position = (0., state['height'], 0.)
            ground = tuple(scene.ground_function(*p) for p in
                vehicle_physics.suspension_world_points(params, position, 0., state['pitch'], state['roll']))
            pseudo = tuple(scene.ground_function(*p) for p in
                vehicle_physics.suspension_pseudo_world_points(params, position, 0., state['pitch'], state['roll']))
            state = vehicle_physics.damper_suspension_step(params, state, ground, 1. / 30., pseudo)
        scene.position = (0., state['height'], 0.)
        battle.local_pose = lambda: (scene.position, scene.flat_body.yaw)
        for body in (scene.flat_body, scene.body):
            body.setRotateYPR((0., state['pitch'], state['roll']))
            body.translation = scene.position
        battle._local_pitch, battle._local_roll = state['pitch'], state['roll']
        battle._local_terrain_pitch = state['pitch']
        plane = vehicle_physics.suspension_world_ground_plane(params, ground, scene.position,
            0., .0001, state['pitch'], state['roll'])
        battle._local_ground_plane = plane
        scene.update_barrel_observation()
        return state

    scene = ActualSiegeAimTests.scene
    # Separate current-mode point projections share the existing stationary
    # frontier/budgets; they are not an additional mode-entry search.
    def test_worker_keeps_motion_only_siege_sample_while_rechecking(self):
        from gui.mods.offline_lan_0922.vehicle_control.bot_binding import BotControlBinding

        scene = self.scene(enabled_pitch=(0., 0.))
        engine, actor = scene.runtime.engine, scene.runtime.actor_id
        state = engine.states[actor]
        records = scene.battle._records
        actor_record = 'bot:%s' % actor
        records[actor_record] = dict(records['player:1'],
            kind='bot', network_id=actor, local=False, state=state)
        self.addCleanup(records.pop, actor_record, None)
        binding = BotControlBinding(scene.battle, engine, actor)
        self.addCleanup(binding.close)
        target = dict(scene.runtime.visible_targets()[0])
        self.assertTrue(binding.observe(scene.now, [target]))
        owner, policy = binding.combat_stop, binding.attack_policy
        owner.active = owner.combat_owned = True
        owner.targets = (target,)
        owner.receipt['selected'] = (target['kind'], target['network_id'])
        policy.frame = policy.evaluator.snapshot(scene.now)
        job = next(job for job in policy._jobs('penetration', binding.gun.shot_index)
                   if job[2]['entity'] is scene.target)
        row = policy._evaluate(job, scene.now, 'foreground')
        policy.decision = dict(action='firing_position', reason='mechanical_limited', candidate=row)
        motion = binding.siege_aim.candidate(policy.frame, scene.now, row)
        self.assertIsNotNone(motion, binding.siege_aim.status())
        binding._siege_aim_candidate = motion
        self.assertIsNone(binding.current_attack_candidate(state, target, for_aim=True))

        with mock.patch.dict(engine._actor_controls, {actor: binding}):
            solution, ready = engine._cadenced_ballistic_solution(
                state, target, engine._descriptors[actor], binding.gun.shot_index, scene.now)
            self.assertTrue(ready)
            self.assertTrue(solution['_player_motion_only'])
            command = dict(fire_allowed=False, _ballistic_solution=solution)
            engine._shared_gun_aim_input(state, command, target, scene.now)

            scene.fixture.now += .1
            scene.pose(scene.target, (0., 13., 100.))
            self.assertTrue(binding.observe(scene.now, [dict(target, position=(0., 13., 100.))]))
            binding._siege_aim_candidate = None
            policy.decision = dict(action='wait', reason='stationary_domain_review_pending', candidate=None)
            waiting = dict(fire_allowed=False)
            retained, contact = engine._shared_gun_aim_input(state, waiting, None, scene.now)
            self.assertIsNotNone(contact)
            self.assertEqual(target['network_id'], contact['network_id'])
            self.assertNotEqual(solution['point'], retained['aim_position'])
            self.assertTrue(retained['_shared_aim_pending'])
            self.assertFalse(retained['fire_allowed'])

            scene.fixture.now += .1
            self.assertTrue(binding.observe(scene.now, []))
            self.assertEqual((waiting, None), engine._shared_gun_aim_input(
                state, waiting, None, scene.now))
            self.assertIsNone(binding._shared_aim_intention)

    def test_worker_complete_support_survives_mode_cache_invalidation(self):
        from gui.mods.offline_lan_0922.vehicle_control.bot_binding import BotControlBinding
        scene = self.scene()
        engine, actor = scene.runtime.engine, scene.runtime.actor_id
        descriptor = scene.entity.typeDescriptor
        engine._descriptor_pairs[actor] = (descriptor, descriptor)
        engine.states[actor]['_edge_support_active'] = True
        descriptor.isPitchHullAimingAvailable = False
        binding = BotControlBinding(scene.battle, engine, actor)
        self.addCleanup(binding.close)
        for mode in (0, 1, 2, 3):
            engine.states[actor]['siege_state'] = mode
            engine._suspension_params.pop(actor, None)
            self.assertTrue(binding.complete_support())

    def test_worker_aim_uses_integrated_descriptor_while_presentation_lags(self):
        from gui.mods.offline_lan_0922.vehicle_control.bot_binding import BotControlBinding
        scene = self.scene()
        engine, actor = scene.runtime.engine, scene.runtime.actor_id
        native = engine._descriptors[actor]
        self.assertIs(native, scene.enabled_descriptor)
        key = 'bot:%s' % actor
        scene.battle._records[key] = dict(scene.battle._records['player:1'],
            kind='bot', network_id=actor, local=False, state=engine.states[actor])
        self.addCleanup(scene.battle._records.pop, key, None)
        binding = BotControlBinding(scene.battle, engine, actor)
        self.addCleanup(binding.close)
        target = dict(scene.runtime.visible_targets()[0])
        self.assertTrue(binding.observe(scene.now, [target]))
        binding.combat_stop.active = binding.combat_stop.combat_owned = True
        binding.combat_stop.targets = (target,)
        frames = []
        # The network/rendered Vehicle can expose an earlier mode or a fresh
        # descriptor object. Neither changes the worker's integrated gun.
        for shown in (scene.enabled_descriptor, scene.travel_descriptor,
                      scene.enabled_descriptor):
            scene.entity.typeDescriptor = shown
            frame = binding.attack_policy.evaluator.snapshot(scene.now)
            self.assertIs(native, frame['descriptor'])
            self.assertIsNotNone(active_hydraulic_pose(binding, frame))
            frames.append(frame)
            scene.fixture.now += .11
        self.assertEqual(frames[0]['identity'], frames[1]['identity'])
        self.assertEqual(frames[0]['identity'], frames[2]['identity'])
        # Presentation cannot manufacture a completed physical mode switch.
        engine.states[actor]['siege_state'] = 1
        frame = binding.attack_policy.evaluator.snapshot(scene.now)
        self.assertIsNone(active_hydraulic_pose(binding, frame))

    def test_all_known_nonpenetrating_he_points_can_close_then_fallback(self):
        scene = self.scene(enabled_pitch=(-.2, .2), clip=3)
        scene.set_he(piercing=0.)
        scene.runtime.gun.ammo[1] = 0
        for name in ('chassis', 'hull', 'turret', 'gun'):
            getattr(scene.target.typeDescriptor, name).materials[0].armor = 10000.
        policy = scene.runtime.attack_policy
        policy.evaluator.atomic_clock = lambda: 0.
        for unused in range(160):
            scene.observe()
            decision = policy.update(scene.now)
            policy.background(scene.now)
            if decision.get('mode') == 'he_fallback' or (
                    decision.get('candidate') or {}).get('mode') == 'he_fallback':
                break
            scene.fixture.now += .11
        else:
            self.fail('actual hydraulic finite domain never closed: %r' % policy.status())
        counts = policy._failure_domain((0,))
        self.assertTrue(counts['all_failed'], counts)
        self.assertGreater(counts['failed'], 0)
        self.assertEqual(0., scene.battle._local_siege_aim_pitch)


if __name__ == '__main__':
    unittest.main()
