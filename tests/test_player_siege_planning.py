"""Active hydraulic aim/finite-TD proofs, never prospective mode admission.

Native observation fixtures feed production policy, source inversion,
stationary collision certificates and hydraulic actuation. These tests do
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
from test_player_stationary_plan import install_plan_observations, NativePlanScene
from gui.mods.offline_lan_0922 import shot_geometry, siege_mechanics, tank_collision, vehicle_physics
from gui.mods.offline_lan_0922.vehicle_control import siege_planning
from gui.mods.offline_lan_0922.vehicle_control.native_aim import (
    active_hydraulic_pose, hydraulic_body, hydraulic_reach, mechanical_reach)


class ActualHydraulicScene(SiegeScene):
    def configure_plan(self, **kwargs):
        self.configure(**kwargs)
        enabled = self.entity.siegeState
        self.position = (0., 0., 0.)
        self.plan_receipts = []
        install_plan_observations(self)
        self.entity.siegeState = enabled
        self.observe()
        return self

    plan_frame = NativePlanScene.plan_frame
    plan = NativePlanScene.plan

    def evaluated_row(self, sample=0, mode='penetration'):
        policy = self.runtime.attack_policy
        self.observe()
        policy.frame = policy.evaluator.snapshot(self.now)
        job = next(job for job in policy._jobs(mode, self.runtime.gun.shot_index)
                   if job[2]['entity'] is self.target and job[3] == sample)
        return policy._evaluate(job, self.now, 'foreground')


class ActualSiegeAimTests(unittest.TestCase):
    def scene(self, **kwargs):
        scene = ActualHydraulicScene()
        scene.setUp()
        self.addCleanup(scene.doCleanups)
        return scene.configure_plan(**kwargs)

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

    def test_disabled_mode_never_inspects_targets_or_native_sources(self):
        scene = self.scene(enabled=False)
        frame = scene.runtime.attack_policy.evaluator.snapshot(scene.now)
        with mock.patch.object(scene.battle._runtime, 'get_shot_angles') as angles:
            self.assertIsNone(scene.runtime.siege_aim.candidate(frame, scene.now))
        angles.assert_not_called()
        self.assertEqual('inactive', scene.runtime.siege_aim.status()['status'])

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

    def test_all_point_certificate_progress_does_not_start_point_by_point_hydraulic_motion(self):
        scene = self.scene()
        row = scene.evaluated_row()
        policy = scene.runtime.attack_policy
        policy.selected = row['key']
        policy.decision = dict(action='wait', reason='stationary_domain_review_pending')
        self.assertIsNone(scene.runtime.siege_aim.candidate(policy.frame, scene.now))

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
    def test_zero_pitch_hydraulic_samples_close_independently_without_moving_actor(self):
        scene = self.scene(enabled_pitch=(0., 0.), hydraulic_center=1.5)
        original = scene.body.yaw, scene.body.pitch, tuple(scene.body.translation)
        corrections = []
        for sample in (0, 1, 2, 3):
            frame, plan = scene.plan(sample=sample)
            self.assertEqual('proved', plan['status'], plan)
            self.assertFalse(plan['proof']['fire_permission'])
            self.assertIsNotNone(plan['proof']['hydraulic'])
            solution = plan['prediction']['solution']
            self.assertTrue(solution['needs_hydraulic'])
            self.assertFalse(solution['source_verified'])
            corrections.append(solution['hydraulic_pitch'])
            self.assertTrue(scene.planner.current(frame, plan['proof']))
            scene.fixture.now += .11
        self.assertGreater(len(set(round(v, 5) for v in corrections)), 1)
        self.assertEqual(original, (scene.body.yaw, scene.body.pitch, tuple(scene.body.translation)))

    def test_hydraulic_contact_blocked_is_pending_not_armour_failure(self):
        scene = self.scene(enabled_pitch=(0., 0.), hydraulic_center=1.5)
        with mock.patch.object(scene.runtime.geometry, '_turret_motion_is_clear', return_value=False):
            frame, plan = scene.plan()
            row = scene.evaluated_row()
        self.assertEqual('pending', plan['status'])
        self.assertEqual('stationary_hydraulic_sweep_blocked', plan['reason'])
        self.assertEqual('unknown', row['armor'])
        self.assertNotEqual('excluded', row.get('scope'))

    def test_outside_hydraulic_range_stays_explicitly_unreachable(self):
        scene = self.scene(enabled_pitch=(0., 0.))
        scene.pose(scene.target, (0., 80., 100.))
        unused, plan = scene.plan()
        self.assertEqual('pending', plan['status'])
        self.assertEqual('stationary_hydraulic_pitch_unreachable', plan['reason'])

    def test_actual_pitch_change_retires_old_stationary_receipt(self):
        scene = self.scene(enabled_pitch=(0., 0.))
        frame, plan = scene.plan()
        self.assertEqual('proved', plan['status'], plan)
        scene.battle._local_siege_aim_pitch = -.1
        self.assertFalse(scene.planner.current(frame, plan['proof']))

    def test_active_hydraulic_yaw_uses_existing_shortest_arc_and_flat_support(self):
        scene = self.scene(enabled_pitch=(0., 0.), hydraulic_center=-1.5)
        scene.pose(scene.target, (math.sin(.6) * 100., 12., math.cos(.6) * 100.))
        frame, plan = scene.plan()
        self.assertEqual('proved', plan['status'], plan)
        self.assertTrue(plan['proof']['arc'])
        self.assertGreater(plan['prediction']['solution']['hull_yaw'], .5)
        self.assertTrue(plan['prediction']['solution']['needs_hydraulic'])
        self.assertTrue(all(receipt['hydraulic']['native_clear'] for receipt in plan['proof']['arc']))
        self.assertAlmostEqual(0., plan['proof']['source_support']['pitch'])
        self.assertLess(sum(abs(receipt['end_yaw'] - receipt['start_yaw'])
                            for receipt in plan['proof']['arc']), math.pi)

    def test_hydraulic_turn_rechecks_the_complete_chassis_on_uneven_ground(self):
        scene = self.scene(enabled_pitch=(0., 0.), hydraulic_center=1.5)
        descriptor = scene.entity.typeDescriptor
        width, length = tank_collision.chassis_shape(descriptor)[:2]
        scene.ground_function = lambda x, z: .02 * x + .07 * (z / length) ** 2
        battle = scene.battle
        accepted = self.complete_ground_pose(scene)
        scene.pose(scene.target, (math.sin(-.7) * 100., 8., math.cos(-.7) * 100.))
        scene.ground_calls.clear()
        frame, plan = scene.plan()
        self.assertEqual('proved', plan['status'], plan)
        proof = plan['proof']
        self.assertEqual('full_chassis_contacts', proof['source_support']['kind'])
        self.assertAlmostEqual(accepted['pitch'], proof['source_support']['pitch'], places=5)
        self.assertAlmostEqual(accepted['roll'], proof['source_support']['roll'], places=5)
        self.assertGreaterEqual(len(scene.ground_calls), 22)
        self.assertLess(plan['flat_body'][0], -.5)
        self.assertNotAlmostEqual(scene.position[1], proof['projected_position'][1])
        # Independent complete-contact projections retain the native 0.1 mm
        # position contract; they need not produce identical floating bits.
        self.assertLessEqual(abs(proof['arc'][-1]['support'][-1]['center_y'] -
                                 proof['projected_position'][1]), .0001)
        self.assertIsNone(battle._local_legacy_support_sample)
        self.assertFalse(proof['fire_permission'])
        self.assertTrue(scene.planner.current(frame, proof))

    def test_hydraulic_review_does_not_admit_missing_midpoint_support(self):
        scene = self.scene(enabled_pitch=(0., 0.))
        scene.pose(scene.target, (math.sin(.6) * 100., 12., math.cos(.6) * 100.))
        params = vehicle_physics.derive_suspension_params(scene.entity.typeDescriptor)
        angle = math.pi / 72.
        missing = (vehicle_physics.suspension_world_points(params, scene.position, angle) +
                   vehicle_physics.suspension_pseudo_world_points(params, scene.position, angle))
        scene.ground_function = lambda x, z: (None if any(
            math.hypot(x - px, z - pz) < .001 for px, pz in missing) else 0.)
        unused, plan = scene.plan()
        self.assertEqual('pending', plan['status'])
        self.assertEqual('stationary_native_support_pending', plan['reason'])
        self.assertFalse(scene.catalog_calls)

    def test_worker_binding_proves_the_same_complete_hydraulic_turn(self):
        from gui.mods.offline_lan_0922.vehicle_control.bot_binding import BotControlBinding
        from gui.mods.offline_lan_0922.vehicle_control.stationary_plan import StationaryPlanner
        scene = self.scene(enabled_pitch=(0., 0.), hydraulic_center=1.5)
        descriptor = scene.entity.typeDescriptor
        width, length = tank_collision.chassis_shape(descriptor)[:2]
        scene.ground_function = lambda x, z: .02 * x + .07 * (z / length) ** 2
        battle = scene.battle
        accepted = self.complete_ground_pose(scene)
        scene.pose(scene.target, (math.sin(-.7) * 100., 8., math.cos(-.7) * 100.))
        scene.observe()
        engine, actor = scene.runtime.engine, scene.runtime.actor_id
        engine.states[actor]['_edge_support_active'] = True
        record = dict(battle._records['player:1'], kind='bot', network_id=actor,
                      local=False, state=engine.states[actor])
        battle._records['bot:%s' % actor] = record
        self.addCleanup(battle._records.pop, 'bot:%s' % actor, None)
        binding = BotControlBinding(battle, engine, actor)
        self.addCleanup(binding.close)
        target = dict(scene.runtime.visible_targets()[0])
        self.assertTrue(binding.observe(scene.now, [target]))
        binding.combat_stop.active = binding.combat_stop.combat_owned = True
        binding.combat_stop.targets = (target,)
        planner = StationaryPlanner(binding)
        planner.clock = lambda: 0.
        state_before = dict(binding.state)
        scene.ground_calls.clear()
        for unused in range(30):
            evaluator = binding.attack_policy.evaluator
            frame = evaluator.snapshot(scene.now)
            observed = next(row for row in frame['targets'] if row['entity'] is scene.target)
            raw = evaluator._prediction(frame, frame['shells'][0], observed, 0)
            plan = planner.project(frame, frame['shells'][0], observed, raw, scene.now, 'foreground')
            if plan['status'] == 'proved' or not plan.get('progressing'):
                break
            scene.fixture.now += .11
        self.assertEqual('proved', plan['status'], plan)
        self.assertEqual('full_chassis_contacts', plan['proof']['source_support']['kind'])
        self.assertAlmostEqual(accepted['pitch'], plan['proof']['source_support']['pitch'], places=5)
        self.assertAlmostEqual(accepted['roll'], plan['proof']['source_support']['roll'], places=5)
        self.assertGreaterEqual(len(scene.ground_calls), 22)
        self.assertLess(plan['flat_body'][0], -.5)
        self.assertTrue(plan['proof']['arc'])
        self.assertTrue(all(row['hydraulic']['native_clear'] for row in plan['proof']['arc']))
        self.assertFalse(plan['proof']['fire_permission'])
        self.assertTrue(planner.current(frame, plan['proof']))
        self.assertEqual(state_before, dict(binding.state))

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

    def test_travel_mode_uses_real_basic_contacts_over_a_supported_step(self):
        from gui.mods.offline_lan_0922.vehicle_control.bot_binding import BotControlBinding
        from gui.mods.offline_lan_0922.vehicle_control.stationary_plan import StationaryPlanner
        from test_player_siege_engagement import pitch_limits
        scene = self.scene(enabled=False)
        # Isolate chassis proof from the gun's pitch restriction. The physical
        # five contacts accept this small step; an independent coplanar fit
        # rejects it even though no witness is missing.
        scene.entity.typeDescriptor.gun.pitchLimits = pitch_limits(-.35, .35)
        scene.ground_function = lambda x, z: .02 if z > 1. else 0.
        scene.pose(scene.target, (math.sin(.7) * 100., 0., math.cos(.7) * 100.))
        scene.observe()
        engine, actor = scene.runtime.engine, scene.runtime.actor_id
        engine.states[actor].pop('_edge_support_active', None)
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
        self.assertFalse(binding.complete_support())
        planner = StationaryPlanner(binding)
        planner.clock = lambda: 0.
        before = dict(binding.state)
        for unused in range(30):
            evaluator = binding.attack_policy.evaluator
            frame = evaluator.snapshot(scene.now)
            observed = next(row for row in frame['targets'] if row['entity'] is scene.target)
            shell = frame['shells'][0]
            raw = evaluator._prediction(frame, shell, observed, 0)
            plan = planner.project(frame, shell, observed, raw, scene.now, 'foreground')
            if plan['status'] == 'proved' or not plan.get('progressing'):
                break
            scene.fixture.now += .11
        self.assertEqual('proved', plan['status'], plan)
        self.assertEqual('basic_chassis_contacts', plan['proof']['source_support']['kind'])
        self.assertTrue(plan['proof']['arc'])
        self.assertFalse(plan['proof']['fire_permission'])
        self.assertEqual(before, dict(binding.state))
        # Identical supported endpoints cannot conceal a missing witness in
        # the middle of the turn. This still runs the physical basic sampler.
        angle = math.pi / 36. * 3.5
        length = max(1.5, float(binding.state.get('half_length', 3.5)))
        missing = (math.sin(angle) * length, math.cos(angle) * length)
        scene.ground_function = lambda x, z: (None if
            math.hypot(x - missing[0], z - missing[1]) < .01 else 0.)
        planner = StationaryPlanner(binding)
        planner.clock = lambda: 0.
        for unused in range(30):
            plan = planner.project(frame, shell, observed, raw, scene.now, 'foreground')
            if not plan.get('progressing'):
                break
            scene.fixture.now += .11
        self.assertEqual('pending', plan['status'], plan)
        self.assertEqual('stationary_native_support_pending', plan['reason'])

    def test_rejected_endpoint_angles_are_logged_only_when_checked(self):
        from gui.mods.offline_lan_0922.vehicle_control import stationary_plan
        for enabled in ('0', '1'):
            with self.subTest(detailed=enabled):
                scene = self.scene()
                frame, shell, target, raw = scene.plan_frame()
                reach = stationary_plan.mechanical_reach
                def refused(*args, **kwargs):
                    return dict(reach(*args, **kwargs), reachable=False)
                with mock.patch.dict(os.environ, {'WOT_OFFLINE_DIAGNOSTICS': '1',
                        'WOT_OFFLINE_COMBAT_DIAGNOSTICS': enabled}), \
                        mock.patch.object(stationary_plan, 'mechanical_reach', refused), \
                        mock.patch('gui.mods.offline_lan_0922.native_input_diagnostics.write_json_record') as emit:
                    with self.assertRaises(stationary_plan._Deferred) as raised:
                        scene.planner._project_point(frame, shell, target, raw,
                            dict(rotationIsAroundCenter=True))
                self.assertEqual('stationary_projected_pitch_pending', raised.exception.reason)
                rows = [call.args[1] for call in emit.call_args_list
                        if call.args[0] == 'BATTLE REVIEW' and
                        call.args[1].get('stage') == 'stationary_endpoint_rejected']
                self.assertEqual(1 if enabled == '1' else 0, len(rows))
                if rows:
                    self.assertFalse(rows[0]['reach']['reachable'])
                    self.assertIn('projected_body', rows[0])

    def test_chassis_collision_surfaces_require_detailed_diagnostics(self):
        for enabled in ('0', '1'):
            with self.subTest(detailed=enabled):
                scene = self.scene(enabled_pitch=(0., 0.))
                output = StringIO()
                with mock.patch.dict(os.environ, {'WOT_OFFLINE_DIAGNOSTICS': '1',
                                                  'WOT_OFFLINE_COMBAT_DIAGNOSTICS': enabled}):
                    with redirect_stdout(output), mock.patch(
                            'gui.mods.offline_lan_0922.native_input_diagnostics.write_json_record') as emit:
                        unused, plan = scene.plan()
                self.assertEqual('proved', plan['status'], plan)
                rows = [call.args[1] for call in emit.call_args_list
                        if call.args[0] == 'BATTLE REVIEW' and
                        call.args[1].get('stage') == 'stationary_chassis_support']
                if enabled == '0':
                    self.assertEqual([], rows)
                    continue
                self.assertTrue(rows)
                self.assertEqual(22, len(rows[0]['columns']))
                self.assertEqual({'spring', 'pseudo'},
                                 {col['family'] for col in rows[0]['columns']})
                self.assertTrue(all(col['layers'][0]['normal'] == [0., 1., 0.]
                                    for col in rows[0]['columns']))

    def test_blocked_shortest_active_arc_never_retries_reverse_long_arc(self):
        scene = self.scene(enabled_pitch=(0., 0.))
        scene.pose(scene.target, (math.sin(.6) * 100., 12., math.cos(.6) * 100.))
        scene.catalog_status = 'hard'
        unused, plan = scene.plan()
        self.assertEqual('pending', plan['status'], plan)
        self.assertEqual('stationary_native_rotation_blocked', plan['reason'])
        self.assertFalse(plan['proved'])
        self.assertTrue(scene.catalog_calls)

    def test_all_known_nonpenetrating_he_points_can_close_then_fallback(self):
        scene = self.scene(enabled_pitch=(0., 0.), clip=3)
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
        self.assertGreater(counts['projected_failed'], 0)
        self.assertEqual(0., scene.battle._local_siege_aim_pitch)


if __name__ == '__main__':
    unittest.main()
