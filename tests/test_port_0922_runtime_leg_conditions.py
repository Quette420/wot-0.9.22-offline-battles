"""Report 182624: an expired bridge/bypass point cannot keep steering."""
import contextlib
import io
import json
import math
import os
import unittest
from unittest import mock

import test_port_0922_bot_runtime as fixtures


GOAL = (204.146, 0., 208.395)
ENTRY = (226.4575879518632, -11.332528777704532, 219.28787882605016)
ENTRY_YAW = -1.9912030108
STALL = (218.05882617138263, -10.92275531629592, 215.9545866615458)
OLD_POINT = (221.2158791394643, -11.003, 213.2158791394643)
SHAPE = (1.8375270366668701, 1.649999976158142)


class RuntimeLegConditionTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.BotRuntimeTests()
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        self.module = fixture.module
        from gui.mods.offline_lan_0922.ai.navigation import TerrainNavigator
        self.navigator_type = TerrainNavigator
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def navigator(self, actor, graph=None):
        if graph is None:
            graph = json.loads((fixtures.ROOT/'navgraphs/84_winter.json').read_text())
        nav = self.navigator_type(lambda *args: None, lambda *args: False, baked_graph=graph)
        nav.bot_states[actor] = dict(request_key=('captured', actor),
            request_path_key=('route', 1, 'bridge', 2), planned_goal=GOAL,
            navigation_status='safe')
        return nav

    def remember_passage(self, nav, actor, point=OLD_POINT):
        # Reconstruct the issued endpoint independently of the new publication
        # API so the captured stale-owner assertion also fails on old code.
        nav.remember_runtime_target(actor, ENTRY, GOAL, point, 161.182)
        state = nav.bot_states[actor]
        state['runtime_target_owner'] = dict(kind='narrow_passage',
            base_target=GOAL, shape=SHAPE)
        state['narrow_passage_target'] = dict(point=point, shape=SHAPE,
            axis=(-2.**-.5, -2.**-.5))
        return state

    def runtime(self, actor, nav):
        runtime = self.module.BotRuntime(1)
        from gui.mods.offline_lan_0922.ai.adapter import BotAdapter
        runtime.adapter = BotAdapter('84_winter', 1)
        runtime.navigator = nav
        runtime.baked_graph = None
        runtime._navigation_height_columns = None
        runtime._route_lane_target = lambda bot, pos, goal, target, *args: target
        runtime.states[actor] = dict(id=actor, team=1, yaw=ENTRY_YAW,
            half_length=SHAPE[0], half_width=SHAPE[1])
        return runtime

    def test_captured_tail_exit_keeps_actual_heading_instead_of_rear_cell_axis(self):
        nav = self.navigator(7)
        result = nav.narrow_passage_target(7, ENTRY, GOAL, GOAL, 161.182,
                                          ENTRY_YAW, *SHAPE)
        self.assertNotEqual(GOAL, result)
        dx, dz = result[0]-ENTRY[0], result[2]-ENTRY[2]
        self.assertAlmostEqual(0., dx*math.cos(ENTRY_YAW)-dz*math.sin(ENTRY_YAW), places=6)
        self.assertGreater(dx*math.sin(ENTRY_YAW)+dz*math.cos(ENTRY_YAW), 0.)
        self.assertNotEqual(OLD_POINT, result)
        self.assertTrue(nav.bot_states[7]['narrow_passage_receipt']['proof']['clear'])

    def test_captured_full_exit_retires_old_point_for_both_actor_identities(self):
        for actor in (6, 1000001):
            with self.subTest(actor=actor):
                nav = self.navigator(actor)
                state = self.remember_passage(nav, actor)
                result = nav.retained_local_target(actor, STALL, GOAL,
                    state['request_path_key'], 166.663, yaw=2.654007664)
                self.assertIsNone(result)
                self.assertNotIn('local_fallback_target', state)
                self.assertNotIn('narrow_passage_target', state)
                self.assertNotIn('last_target', state)
                self.assertEqual('body_clear_of_passage', state['runtime_target_release']['reason'])

    def test_still_narrow_retains_endpoint_and_pending_proof_does_not_expire_it(self):
        for deferred in (False, True):
            with self.subTest(deferred=deferred):
                nav = self.navigator(7)
                state = self.remember_passage(nav, 7)
                def proof(*args):
                    self.assertEqual(7, nav._boundary_actor)
                    if deferred:
                        nav.grid._native_proof_revision += 1
                    return not deferred
                nav._boundary_actor = 7
                with mock.patch.object(nav.grid, 'dry_segment_clear', side_effect=proof):
                    result = nav.retained_local_target(7, ENTRY, GOAL,
                        state['request_path_key'], 161.4, yaw=ENTRY_YAW)
                self.assertEqual(ENTRY if deferred else OLD_POINT, result)
                self.assertEqual(OLD_POINT, state['local_fallback_target'])
                self.assertIn('narrow_passage_target', state)

    def test_runtime_exit_selects_new_checked_leg_and_releases_matching_alignment(self):
        for actor in (6, 1000001):
            with self.subTest(actor=actor):
                nav = self.navigator(actor)
                self.remember_passage(nav, actor)
                runtime = self.runtime(actor, nav)
                from gui.mods.offline_lan_0922.ai.driver import LocalDriver
                driver = LocalDriver()
                runtime.adapter.driver = driver
                driver.states[actor] = dict(alignment_target=OLD_POINT)
                # A newly proved corner may be within the driver's ordinary
                # two-metre leg identity: expiry must still drop the old lease.
                corner = (OLD_POINT[0]-.5, OLD_POINT[1], OLD_POINT[2]+.5)
                def choose(*args, **kwargs):
                    self.assertNotIn('local_fallback_target', nav.bot_states[actor])
                    return corner
                with mock.patch.object(nav, 'next_target', side_effect=choose) as select:
                    result = runtime._navigation_target_impl(actor, STALL, GOAL,
                        dict(combat_mode='route', route_id='bridge', route_index=2),
                        dict(now=166.663, yaw=2.654007664, speed=0.,
                             half_length=SHAPE[0], half_width=SHAPE[1]))
                select.assert_called_once()
                self.assertEqual(corner, result)
                self.assertNotIn('alignment_target', driver.states[actor])
                self.assertTrue(runtime.states[actor]['_navigation_target_receipt']
                    ['retired_runtime_target']['alignment_released'])

    def test_runtime_pending_proof_keeps_passage_memory_without_new_movement(self):
        nav = self.navigator(7)
        state = self.remember_passage(nav, 7)
        runtime = self.runtime(7, nav)
        def deferred(*args):
            nav.grid._native_proof_revision += 1
            return False
        with mock.patch.object(nav.grid, 'dry_segment_clear', side_effect=deferred):
            result = runtime._navigation_target_impl(7, ENTRY, GOAL,
                dict(combat_mode='route', route_id='bridge', route_index=2),
                dict(now=161.3, yaw=ENTRY_YAW, speed=0.,
                     half_length=SHAPE[0], half_width=SHAPE[1]))
        self.assertEqual(ENTRY, result)
        self.assertEqual('pending', state['navigation_status'])
        self.assertEqual(OLD_POINT, state['local_fallback_target'])
        self.assertIn('narrow_passage_target', state)
        self.assertNotIn('runtime_target_release', state)

    def test_tail_heading_still_requires_fresh_native_corridor_and_support(self):
        for refusal in ('native', 'support', 'deferred'):
            with self.subTest(refusal=refusal):
                nav = self.navigator(7)
                def proof(*args):
                    if refusal == 'deferred':
                        nav.grid._native_proof_revision += 1
                    return False
                with mock.patch.object(nav.grid, 'dry_segment_clear', side_effect=proof), \
                        mock.patch.object(nav.grid, 'hull_pose_clear', return_value=refusal != 'support'):
                    result = nav.narrow_passage_target(7, ENTRY, GOAL, GOAL,
                        161.182, ENTRY_YAW, *SHAPE)
                self.assertEqual(GOAL, result)
                self.assertNotIn('narrow_passage_target', nav.bot_states[7])

    def test_expiry_does_not_clear_another_alignment_or_grant_a_pending_leg(self):
        nav = self.navigator(7)
        self.remember_passage(nav, 7)
        runtime = self.runtime(7, nav)
        from gui.mods.offline_lan_0922.ai.driver import LocalDriver
        driver = LocalDriver()
        runtime.adapter.driver = driver
        other = (250., -11., 240.)
        driver.states[7] = dict(alignment_target=other)
        def pending(*args, **kwargs):
            nav.bot_states[7]['navigation_status'] = 'pending'
            return STALL
        with mock.patch.object(nav, 'next_target', side_effect=pending):
            result = runtime._navigation_target_impl(7, STALL, GOAL,
                dict(combat_mode='route', route_id='bridge', route_index=2),
                dict(now=166.663, yaw=2.654007664, speed=0.))
        self.assertEqual(STALL, result)
        self.assertEqual('pending', nav.bot_states[7]['navigation_status'])
        self.assertEqual(other, driver.states[7]['alignment_target'])

    def test_passage_end_does_not_retire_an_unrelated_local_escape(self):
        nav = self.navigator(7)
        state = self.remember_passage(nav, 7)
        state['runtime_target_owner'] = dict(kind='occupied_route', base_target=GOAL)
        nav.end_narrow_passage(7, 162., 'navigation_owner_changed')
        self.assertEqual(OLD_POINT, state['local_fallback_target'])
        self.assertNotIn('narrow_passage_target', state)

    def test_source_and_expiry_logs_require_the_detailed_diagnostics_option(self):
        for enabled in (False, True):
            with self.subTest(enabled=enabled):
                output = io.StringIO()
                with mock.patch.dict(os.environ, WOT_OFFLINE_DIAGNOSTICS='1' if enabled else '0'), \
                        contextlib.redirect_stdout(output):
                    nav = self.navigator(7)
                    state = self.remember_passage(nav, 7)
                    nav.retained_local_target(7, STALL, GOAL,
                        state['request_path_key'], 166.663, yaw=2.654007664)
                self.assertEqual(enabled, 'BOT LOCAL HANDOFF' in output.getvalue())
                if not enabled:
                    self.assertEqual('', output.getvalue())

    def occupied_scene(self, actor):
        nav = self.navigator(actor, fixtures._flat_open_graph())
        runtime = self.runtime(actor, nav)
        position, goal, corner = (0., 0., 0.), (0., 0., 40.), (0., 0., 8.)
        state = nav.bot_states[actor]
        state.update(planned_goal=goal, request_path_key=('route', 1, 'bridge', 2))
        runtime._physical_parking_occupancy = mock.Mock(return_value=[(None, corner, 3.5)])
        def choose(bot, pos, target, path_key, *args, **kwargs):
            state.update(request_path_key=tuple(path_key), planned_goal=target,
                         navigation_status='safe', last_target=corner)
            return corner
        nav.next_target = mock.Mock(side_effect=choose)
        order = dict(combat_mode='route', route_id='bridge', route_index=2)
        decision = dict(now=1., yaw=0., speed=0.)
        first = runtime._navigation_target_impl(actor, position, goal, order, decision)
        self.assertNotEqual(corner, first)
        self.assertEqual(first, state['local_fallback_target'])
        self.assertEqual('occupied_route', state['runtime_target_owner']['kind'])
        self.assertEqual(corner, state['runtime_target_owner']['base_target'])
        return runtime, nav, goal, corner, first, order

    def test_original_local_endpoint_is_rechecked_even_with_a_retained_bypass(self):
        for actor in (6, 1000001):
            with self.subTest(actor=actor):
                runtime, nav, goal, corner, first, order = self.occupied_scene(actor)
                position = (0., 0., 1.)
                kept = runtime._navigation_target_impl(actor, position, goal, order,
                    dict(now=2., yaw=0., speed=0.))
                self.assertEqual(first, kept)
                self.assertEqual(1, nav.next_target.call_count)
                runtime._physical_parking_occupancy.return_value = []
                selected = runtime._navigation_target_impl(actor, position, goal, order,
                    dict(now=3., yaw=0., speed=0.))
                self.assertEqual(corner, selected)
                self.assertEqual(2, nav.next_target.call_count)
                self.assertNotIn('local_fallback_target', nav.bot_states[actor])
                self.assertEqual('occupied_endpoint_clear', runtime.states[actor]
                    ['_navigation_target_receipt']['retired_runtime_target']['reason'])

    def test_new_passage_point_publishes_source_and_own_endpoint_keeps_its_owner(self):
        nav = self.navigator(7)
        runtime = self.runtime(7, nav)
        def choose(bot, position, goal, key, *args, **kwargs):
            nav.bot_states[bot].update(request_path_key=key, navigation_status='safe')
            return GOAL
        with mock.patch.object(nav, 'next_target', side_effect=choose):
            state = dict(now=161.182, yaw=ENTRY_YAW, speed=0.,
                         half_length=SHAPE[0], half_width=SHAPE[1])
            order = dict(combat_mode='route', route_id='bridge', route_index=2)
            target = runtime._navigation_target_impl(7, ENTRY, GOAL, order, state)
            self.assertEqual('narrow_passage', nav.bot_states[7]['runtime_target_owner']['kind'])
            self.assertEqual(target, nav.bot_states[7]['narrow_passage_target']['point'])
            again = runtime._navigation_target_impl(7, ENTRY, GOAL, order, dict(state, now=161.3))
            self.assertEqual(target, again)
            self.assertIn('narrow_passage_target', nav.bot_states[7])


if __name__ == '__main__':
    unittest.main()
