'''Turn evaluation uses the observed vehicle and leaves first-edge admission closed.'''
from unittest import TestCase, mock

from test_player_limited_traverse import TraverseScene, install_ground_observations
from test_player_siege_planning import ActualHydraulicScene
from gui.mods.offline_lan_0922.vehicle_control.native_aim import hull_turn_ready


class TurnBeforeShotTests(TestCase):
    def test_sideways_ray_can_request_turn_without_touching_armour_or_future_support(self):
        for scene_type in (TraverseScene, ActualHydraulicScene):
            with self.subTest(vehicle=scene_type.__name__):
                scene = scene_type()
                scene.setUp()
                self.addCleanup(scene.doCleanups)
                if scene_type is TraverseScene:
                    scene.configure(bearing=1.4)
                    install_ground_observations(scene)
                    evaluate = scene.evaluate
                else:
                    scene.configure_hydraulics(enabled_pitch=(0., 0.))
                    scene.pose(scene.target, (100., 12., 0.))
                    evaluate = scene.evaluated_row
                evaluator = scene.runtime.attack_policy.evaluator
                ground_reads, catalog_reads = len(scene.ground_calls), len(scene.catalog_calls)
                with mock.patch.object(evaluator, '_probe_armour') as armour:
                    row = evaluate()
                armour.assert_not_called()
                self.assertEqual(ground_reads, len(scene.ground_calls))
                self.assertEqual(catalog_reads, len(scene.catalog_calls))
                self.assertTrue(hull_turn_ready(row), row)
                self.assertEqual('unknown', row['armor'])
                self.assertFalse(scene.runtime.attack_policy._executable(row))
                self.assertFalse(scene.launches())
