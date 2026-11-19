"""The approved centre-line/chassis gates, independent of point selection."""
import math
import unittest

from gui.mods.offline_lan_0922.vehicle_control.attack_review import AttackReview, geometry


class CombatReviewAngleTests(unittest.TestCase):
    def setUp(self):
        self.review = AttackReview()
        self.key = ('bot', 7)

    def frame(self, line=0., hull=0., loaded=0):
        result = dict(weapon_identity=(1, 123), loaded=loaded,
            review_geometry={self.key: ((math.sin(math.radians(line)), 0., math.cos(math.radians(line))),
                                       math.radians(hull))},
            review_identities={self.key: 77})
        self.review.observe(result)
        return result

    def test_first_complete_observation_establishes_shared_target_anchor(self):
        frame = self.frame()
        self.assertIsNone(self.review.targets[self.key]['anchor'])
        self.assertTrue(self.review.commit(frame, self.key))
        self.assertEqual(((0., 0., 1.), 0.), self.review.targets[self.key]['anchor'])

    def test_small_changes_accumulate_from_completed_anchor_not_previous_frame(self):
        self.review.commit(self.frame(), self.key)
        for angle in (5., 10., 20., 29.9):
            frame = self.frame(line=angle)
            self.assertEqual(0, frame['review_stamps'][self.key][1])
            self.review.commit(frame, self.key)
        self.assertEqual(1, self.frame(line=30.)['review_stamps'][self.key][1])

    def test_later_other_gate_still_triggers_without_a_permanent_seen_flag(self):
        self.review.commit(self.frame(), self.key)
        first = self.frame(line=30.)
        self.review.commit(first, self.key)
        later = self.frame(line=30., hull=30.)
        self.assertEqual(2, later['review_stamps'][self.key][1])
        self.assertEqual(('enemy_heading',), later['review_reasons'][self.key]['changed'])

    def test_one_pending_review_does_not_restart_on_every_observation(self):
        self.review.commit(self.frame(), self.key)
        first = self.frame(line=30.)
        self.assertEqual(1, first['review_stamps'][self.key][1])
        self.assertEqual(1, self.frame(line=60.)['review_stamps'][self.key][1])
        self.review.commit(first, self.key)
        self.assertEqual(2, self.frame(line=60.)['review_stamps'][self.key][1])

    def test_two_changed_inputs_are_one_target_state_update(self):
        self.review.commit(self.frame(), self.key)
        frame = self.frame(line=30., hull=30.)
        self.assertEqual(1, frame['review_stamps'][self.key][1])
        self.assertEqual(('centre_line', 'enemy_heading'), frame['review_reasons'][self.key]['changed'])

    def test_point_changes_cannot_replace_the_vehicle_anchor(self):
        frame = self.frame()
        self.review.commit(frame, self.key)
        for unused_point in (0, 8, 2, 0):
            self.review.commit(self.frame(line=20.), self.key)
        self.assertEqual(1, self.frame(line=30.)['review_stamps'][self.key][1])

    def test_heading_wrap_uses_smallest_angle(self):
        self.review.commit(self.frame(hull=179.), self.key)
        self.assertEqual(0, self.frame(hull=-179.)['review_stamps'][self.key][1])

    def test_forward_translation_does_not_change_centre_line(self):
        self.assertEqual(geometry((0., 0., 0.), (0., 0., 100.), 0.),
                         geometry((0., 0., 20.), (0., 0., 150.), 0.))

    def test_centre_line_uses_the_world_direction_including_vertical_movement(self):
        from gui.mods.offline_lan_0922.vehicle_control.attack_review import angle_difference
        first = geometry((0., 0., 0.), (0., 0., 100.), 0.)
        second = geometry((0., 0., 0.), (0., 100. * math.tan(math.radians(30.)), 100.), 0.)
        self.assertAlmostEqual(math.radians(30.), angle_difference(first[0], second[0]))

    def test_mounting_a_shell_does_not_erase_other_shell_return_evidence(self):
        first = self.frame(loaded=0)
        self.review.commit(first, self.key)
        second = self.frame(loaded=1)
        self.assertEqual(1, second['review_loads'][1])
        self.assertEqual(0, second['review_loads'].get(0, 0))
        self.assertEqual(first['review_stamps'], second['review_stamps'])

    def test_departure_and_reentry_cannot_resurrect_an_earlier_epoch(self):
        first = self.frame()
        self.review.commit(first, self.key)
        departed = dict(weapon_identity=first['weapon_identity'], loaded=0,
                        review_geometry={}, review_identities={})
        self.review.observe(departed)
        reentered = self.frame()
        self.assertNotEqual(first['review_stamps'], reentered['review_stamps'])


if __name__ == '__main__':
    unittest.main()
