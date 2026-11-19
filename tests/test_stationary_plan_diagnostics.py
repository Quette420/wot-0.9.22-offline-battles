"""Opt-in producer/current/consumer identity without changing native proof."""
import os
import unittest
from unittest import mock

from test_player_stationary_plan import NativePlanScene
from gui.mods.offline_lan_0922.vehicle_control import stationary_plan


class StationaryPlanDiagnosticTests(unittest.TestCase):
    def scene(self):
        scene = NativePlanScene()
        scene.setUp()
        self.addCleanup(scene.doCleanups)
        scene.configure_plan(bearing=.6)
        return scene

    def plan(self, scene):
        for unused in range(100):
            frame, shell, target, raw = scene.plan_frame()
            key = (shell['index'], target['key'], 0, 'penetration')
            result = scene.planner.project(frame, shell, target, raw, scene.now,
                'foreground', diagnostic_key=key)
            if result['status'] == 'proved' or not result.get('progressing'):
                break
            scene.fixture.now += .11
        self.assertEqual('proved', result['status'], result)
        return frame, shell, target, key, result

    def test_disabled_option_adds_no_plan_identity_or_trace(self):
        scene = self.scene()
        with mock.patch.dict(os.environ, WOT_OFFLINE_COMBAT_DIAGNOSTICS='0'), \
                mock.patch.object(stationary_plan, 'combat_detail') as detail:
            frame, shell, target, key, result = self.plan(scene)
            self.assertTrue(scene.planner.current(frame, result['proof']))
            stationary_plan.trace_plan_use(scene.runtime, 'controls',
                dict(key=key, stationary_plan=result), scene.now, 'test')
        detail.assert_not_called()
        self.assertNotIn('diagnostic', result['proof'])
        self.assertFalse(hasattr(scene.planner, '_diagnostic_sequence'))
        self.assertFalse(result['proof']['fire_permission'])

    def test_producer_and_consumer_keep_distinct_modes_on_one_geometry_plan(self):
        scene = self.scene()
        with mock.patch.dict(os.environ, WOT_OFFLINE_COMBAT_DIAGNOSTICS='1'), \
                mock.patch.object(stationary_plan, 'combat_detail') as detail:
            frame, shell, target, key, result = self.plan(scene)
            trace = result['proof']['diagnostic']
            self.assertEqual(key, trace['producer_key'])
            self.assertEqual(shell['index'], trace['shell_index'])
            self.assertEqual(shell['shell_identity'], trace['shell'])
            self.assertEqual(shell['gun_identity'], trace['gun'])
            fallback = key[:3] + ('he_fallback',)
            row = dict(key=fallback, stationary_plan=result)
            stationary_plan.trace_plan_use(scene.runtime, 'siege_selection', row,
                                           scene.now, 'ready')
            payload = detail.call_args[0][5]()
        self.assertEqual(fallback, payload['checked_key'])
        self.assertEqual(key, payload['plan']['producer_key'])
        self.assertEqual(trace['plan_id'], payload['plan']['plan_id'])
        self.assertFalse(result['proof']['fire_permission'])

    def test_current_rejection_names_changed_collision_dependency(self):
        scene = self.scene()
        with mock.patch.dict(os.environ, WOT_OFFLINE_COMBAT_DIAGNOSTICS='1'), \
                mock.patch.object(stationary_plan, 'combat_detail') as detail:
            frame, shell, target, key, result = self.plan(scene)
            self.assertTrue(scene.planner.current(frame, result['proof']))
            scene.scene_revision += 1
            self.assertFalse(scene.planner.current(frame, result['proof']))
            payload = detail.call_args[0][5]()
        self.assertEqual('stationary_plan_current', detail.call_args[0][1])
        self.assertFalse(payload['valid'])
        self.assertIn('collision', payload['changes'])
        check = result['proof']['diagnostic']['last_check']
        self.assertEqual('dependencies_changed', check['reason'])
        self.assertFalse(check['valid'])

    def test_native_unsettled_guard_retains_its_exact_reason_and_refusal(self):
        scene = self.scene()
        with mock.patch.dict(os.environ, WOT_OFFLINE_COMBAT_DIAGNOSTICS='1'), \
                mock.patch.object(stationary_plan, 'combat_detail') as detail:
            frame, shell, target, key, result = self.plan(scene)
            scene.battle._local_vertical_speed = .00002
            self.assertFalse(scene.planner.current(frame, result['proof']))
        check = result['proof']['diagnostic']['last_check']
        self.assertEqual('stationary_native_support_unsettled', check['reason'])
        self.assertFalse(check['valid'])
        self.assertFalse(result['proof']['fire_permission'])


if __name__ == '__main__':
    unittest.main()
