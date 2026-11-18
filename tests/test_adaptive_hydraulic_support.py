"""Support-owner parity and offset endpoint regressions; engine-free evidence."""
import math
import unittest
from unittest import mock

import test_port_0922_bot_runtime as fixture


class AdaptiveSupportTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture.BotRuntimeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_terrain_tilt_admits_full_but_hydraulic_correction_does_not(self):
        slope = [0.]
        runtime, state, unused = self.fixture._suspension_case(lambda x, z: -math.tan(slope[0])*z)
        runtime.states[11] = state
        runtime._descriptors[11].isPitchHullAimingAvailable = True
        state.update(pitch=.3, suspension_pitch=.3, terrain_pitch=0.)
        self.assertIsNone(runtime._suspension_params_for(11))
        slope[0] = .25
        state.update(terrain_pitch=.25, pitch=.55)
        self.assertIsNotNone(runtime._suspension_params_for(11))
        self.assertTrue(state['_edge_support_active'])
        self.assertEqual('terrain_tilt', state['_support_admission_reason'])

    def test_flat_return_waits_stably_and_preserves_pose_and_velocity(self):
        runtime, state, unused = self.fixture._suspension_case(lambda x, z: 0.)
        runtime.states[11] = state
        runtime._descriptors[11].isPitchHullAimingAvailable = True
        state['_edge_support_active'] = True
        state['siege_state'] = 2
        runtime._contact_now = 1.
        self.assertFalse(runtime._release_detailed_support(state))
        state['terrain_pitch'] = .14
        runtime._contact_now = 1.8
        self.assertFalse(runtime._release_detailed_support(state))
        state['terrain_pitch'] = 0.
        runtime._contact_now = 2.
        self.assertFalse(runtime._release_detailed_support(state))
        runtime._contact_now = 2.9
        self.assertFalse(runtime._release_detailed_support(state))
        before = tuple(state[name] for name in ('x','y','z','yaw','pitch','roll','speed','vertical_speed'))
        runtime._contact_now = 3.1
        self.assertTrue(runtime._release_detailed_support(state))
        self.assertEqual(before, tuple(state[name] for name in
            ('x','y','z','yaw','pitch','roll','speed','vertical_speed')))

    def test_stationary_basic_owner_rechecks_witnesses_without_coplanar_fit(self):
        runtime, state, unused = self.fixture._suspension_case(
            lambda x, z: .1 if z > 1. else 0.)
        runtime.states[11] = state
        from gui.mods.offline_lan_0922.vehicle_control.bot_binding import BotControlBinding
        binding = object.__new__(BotControlBinding)
        binding.engine, binding.actor_id = runtime, 11
        self.assertFalse(binding.complete_support())
        trace = []
        result = binding.chassis_support_at((0.,0.,0.), 0., runtime._descriptors[11], None, trace)
        self.assertEqual('basic_chassis_contacts', result['kind'])
        self.assertEqual(5, len(trace))
        runtime._physics_ground_probe = lambda x, z, hint: None if z > 1. else 0.
        self.assertIsNone(binding.chassis_support_at(
            (0.,0.,0.), 0., runtime._descriptors[11], None, None))
        state['_edge_support_active'] = True
        runtime._suspension_params.pop(11, None)
        self.assertTrue(binding.complete_support())

    def test_outer_offset_hands_back_without_reassigning_lane_or_changing_arrival_disk(self):
        module = self.fixture.module
        runtime = module.BotRuntime(1)
        state = dict(id=11, team=1, x=0., y=0., z=0., yaw=0.)
        runtime.states[11] = state
        route = dict(route_id='test', route_index=1, route_anchor=(0.,0.,0.))
        goal = (0.,0.,80.)
        with mock.patch.object(runtime, '_route_lane_binding', return_value=(10.,0.)), \
                mock.patch.object(runtime, '_safe_route_lane_goal', return_value=(10.,0.,80.)):
            first, identity = runtime._route_lane_goal(11, (0.,0.,0.), goal, route, 1., True)
            self.assertEqual((10.,0.,80.), first)
            self.assertEqual((10000,0), identity)
            self.assertGreater(math.hypot(first[0]-goal[0],first[2]-goal[2]),
                               module.bot_tactics.ROUTE_ARRIVAL_RADIUS)
            self.assertEqual((goal,(0,0)), runtime._route_lane_goal(11, first, goal, route, 2., True))
            # Leaving the offset's small disk must not select it again.
            self.assertEqual((goal,(0,0)), runtime._route_lane_goal(
                11, (7.,0.,80.), goal, route, 3., True))
            self.assertEqual((first,identity), runtime._route_lane_goal(
                11, (7.,0.,80.), goal, dict(route,route_index=2), 4., True))
        self.assertEqual(6., module.bot_tactics.ROUTE_ARRIVAL_RADIUS)


if __name__ == '__main__':
    unittest.main()
