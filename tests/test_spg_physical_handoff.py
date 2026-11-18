"""Native-angle and pending-order regressions from S-51 report 034847."""
import unittest
from unittest import mock

import test_port_0922_spg_failed_launch as launch_fixture
from test_shared_artillery_selection import PolicyScene


class PhysicalHandoffTests(unittest.TestCase):
    def setUp(self):
        self.scene = launch_fixture.FailedLaunchTests()
        self.scene.setUp()
        self.addCleanup(self.scene.doCleanups)

    def test_pending_shared_region_stops_deployment_without_withdrawing_fire(self):
        s = self.scene
        s.runtime.spg_reservation_request = lambda state, plan: 'pending'
        s.source.update(profile=dict(class_tag='SPG'), _spg_initial=dict(zone='test'))
        order = dict(combat_mode='artillery_deploy', move_position=(0.,0.,80.),
                     fire_allowed=True, target_id=3, route_join=True)
        held = s.runtime._artillery_position_order(s.source, order, {}, 1.)
        self.assertEqual('artillery_hold', held['combat_mode'])
        self.assertEqual(s.bot_module._position(s.source), held['move_position'])
        self.assertEqual(0., held['throttle_override'])
        self.assertTrue(held['fire_allowed'])
        self.assertFalse(held['route_join'])

    def test_observed_barrel_seeds_exact_proof_despite_native_angle_roundoff(self):
        s = self.scene
        solution = s.controller._candidates(s.source, s.target, s.descriptor, 0)[0]
        s.align(solution)
        s.source.update(turret_yaw=2.e-6, gun_pitch=solution['pitch']+2.e-6)
        actual = s.runtime._exact_shot_direction(s.source, s.descriptor)
        self.assertIsNone(s.receipt(solution, 1.))
        intent = s.runtime._artillery_intents[11]
        expected = s.bot_module._dispersed_barrel_angles(
            11, 7, 1, s.source['aim_yaw'], s.source['gun_pitch'],
            s.bot_module._effective_shot_dispersion(s.gun, s.source, s.descriptor),
            base_direction=actual)
        self.assertEqual(expected, (intent['shot_yaw'], intent['shot_pitch']))
        self.assertEqual(0, s.source['fire_seq'])
        s.prove(1., lambda first, second: None)
        self.assertIsNotNone(s.receipt(solution, 1.05))

    def test_pending_current_review_keeps_frozen_work_without_authorizing_fire(self):
        s = self.scene
        policy = PolicyScene()
        policy.choose()
        s.target.update(kind='bot', network_id=3)
        solution = s.controller._candidates(s.source, s.target, s.descriptor, 0)[0]
        s.align(solution)
        self.assertIsNone(s.receipt(solution, 2.))
        intent = s.runtime._artillery_intents[11]
        policy.values[3] = 'pending'
        policy.now += .3
        command = policy.tick()
        self.assertFalse(command['fire_allowed'])
        self.assertEqual(('bot', 3, 0), command.get('artillery_review_pending'))
        retained, reproof = s.runtime._reconcile_artillery_order(
            s.source, command, s.target, s.descriptor, 0, 2.02)
        self.assertIs(intent, retained)
        self.assertIs(intent, s.runtime._artillery_intents[11])
        self.assertIsNotNone(reproof)
        self.assertIn(11, s.controller._launch_keys)
        self.assertEqual(0, s.source['fire_seq'])
        s.prove(2.02, lambda first, second: None)
        self.assertIsNotNone(s.receipt(solution, 2.05))

    def test_coarse_alignment_cannot_admit_an_observably_different_barrel(self):
        s = self.scene
        solution = s.controller._candidates(s.source, s.target, s.descriptor, 0)[0]
        s.align(solution)
        s.source.update(turret_yaw=.001)
        self.assertIsNone(s.receipt(solution, 1.))
        self.assertNotIn(11, s.runtime._artillery_intents)
        self.assertNotIn(11, s.controller._launch_keys)

    def test_yaw_only_native_roundoff_does_not_reuse_commanded_flat_ray(self):
        s = self.scene
        solution = s.controller._candidates(s.source, s.target, s.descriptor, 0)[0]
        s.align(solution)
        s.source['turret_yaw'] = 2.e-6
        self.assertIsNone(s.receipt(solution, 1.))
        intent = s.runtime._artillery_intents[11]
        actual = s.runtime._exact_shot_direction(s.source, s.descriptor)
        expected = s.bot_module._dispersed_barrel_angles(
            11,7,1,s.source['aim_yaw'],s.source['gun_pitch'],
            s.bot_module._effective_shot_dispersion(s.gun,s.source,s.descriptor),
            base_direction=actual)
        self.assertEqual(expected,(intent['shot_yaw'],intent['shot_pitch']))

    def test_explicit_withdrawal_retires_even_a_pending_current_review(self):
        policy = PolicyScene()
        policy.choose()
        policy.values[3] = 'pending'
        policy.order['fire_allowed'] = False
        policy.now += .3
        command = policy.tick()
        self.assertFalse(command['fire_allowed'])
        self.assertIsNone(command.get('artillery_review_pending'))

    def test_pending_for_another_shell_cannot_keep_the_old_launch(self):
        s = self.scene
        solution = s.controller._candidates(s.source, s.target, s.descriptor, 0)[0]
        s.align(solution)
        self.assertIsNone(s.receipt(solution, 3.))
        result = s.runtime._reconcile_artillery_order(s.source,
            dict(fire_allowed=False, artillery_review_pending=('human', 2, 1)),
            s.target, s.descriptor, 0, 3.01)
        self.assertEqual((None, None), result)
        self.assertNotIn(11, s.runtime._artillery_intents)
        self.assertNotIn(11, s.controller._launch_keys)

    def test_disabled_detail_does_not_collect_preparation_pose(self):
        s = self.scene
        with mock.patch.object(s.bot_module, 'combat_detail_enabled', return_value=False), \
             mock.patch.object(s.runtime, '_artillery_source_pose', side_effect=AssertionError('unchecked detail')), \
             mock.patch.object(s.bot_module, 'combat_detail') as record:
            self.assertIsNone(s.runtime._artillery_prepare_refused(
                s.source, s.target, 0, 4., 'actual_barrel_unavailable'))
        record.assert_not_called()
        self.assertEqual('actual_barrel_unavailable', s.source['_spg_prepare_refusal'])


if __name__ == '__main__':
    unittest.main()
