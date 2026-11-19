"""Player/BOT armour retention, actual obstruction and trigger integration.

Native transforms/collision are controlled fixtures. Actual policy/evaluator,
bindings, trigger admission, gun debits and physical launch ownership run here.
This does not claim Windows native timing or support acceptance.
"""
import contextlib
import io
import math
import unittest
from unittest import mock

import test_player_fire_admission_complete as native
import test_port_0922_actor_binding as actors


class SharedCombatReviewContractTests(unittest.TestCase):
    def fixture(self, bot=False):
        value = (actors.WorkerFirstEdgeAdmissionTests('runTest') if bot else
                 native.AutomaticFireScene('runTest'))
        with contextlib.redirect_stdout(io.StringIO()):
            value.setUp()
        self.addCleanup(value.doCleanups)
        scene = value.scene if bot else value
        runtime = value.binding if bot else value.runtime
        if bot:
            job = self.refresh(value, scene, runtime, bot)
            for unused in range(8):
                row = runtime.attack_policy._evaluate(job, scene.now, 'foreground')
                if row['armor'] == 'passed':
                    break
                job = self.refresh(value, scene, runtime, bot)
            self.assertEqual('passed', row['armor'])
            value.candidate = row
            runtime.attack_policy._choose('aim', 'observed_native_plate', row)
            runtime.weapon.observe(dict(_ballistic_solution=row['solution']), value.target)
        return value, scene, runtime

    def observe_other(self, value, scene, runtime, other, bot):
        if bot:
            row = dict(value.target, id=other.id, network_id=other.id,
                       engine_id=other.id, key=('bot', other.id),
                       position=tuple(other.position), velocity=(0., 0., 0.))
            runtime.observe(scene.now, [value.target, row])

    def refresh(self, value, scene, runtime, bot, sample=None):
        scene.fixture.now += .1
        if bot:
            runtime.observe(scene.now, [value.target])
        else:
            scene.observe()
        policy = runtime.attack_policy
        policy.frame = policy.evaluator.snapshot(scene.now)
        key = value.candidate['key']
        return next(job for job in policy._jobs(key[3], key[0])
                    if job[0][1] == key[1] and job[3] == (key[2] if sample is None else sample))

    def test_aiming_and_small_enemy_motion_reuse_the_actual_armour_decision(self):
        for bot in (False, True):
            with self.subTest(bot=bot), contextlib.redirect_stdout(io.StringIO()):
                value, scene, runtime = self.fixture(bot)
                policy = runtime.attack_policy
                evaluator = policy.evaluator
                if bot:
                    value.state['yaw'] = .2
                    value.state['x'] = .2
                else:
                    scene.body.setRotateYPR((.2, .01, -.01))
                    scene.battle._local_yaw = .2
                scene.pose(scene.target, (1., 0., 105.))
                scene.target.matrix.setRotateY(math.radians(29.9))
                scene.target.matrix.translation = (1., 0., 105.)
                scene.target.appearance.turretMatrix.setRotateY(.7)
                job = self.refresh(value, scene, runtime, bot)
                with mock.patch.object(evaluator, '_armour_geometry',
                                       side_effect=AssertionError('unapproved armour review')):
                    for unused in range(8):
                        row = policy._evaluate(job, scene.now, 'foreground')
                        if row['line'] != 'pending':
                            break
                        job = self.refresh(value, scene, runtime, bot)
                self.assertEqual('passed', row['armor'])
                self.assertFalse(policy.frame['review_reasons'])

    def test_enemy_heading_threshold_reopens_all_points_but_point_selection_does_not(self):
        for bot in (False, True):
            with self.subTest(bot=bot), contextlib.redirect_stdout(io.StringIO()):
                value, scene, runtime = self.fixture(bot)
                policy = runtime.attack_policy
                old = value.candidate['pose_stamp']
                scene.pose(scene.target, (0., 0., 100.))
                scene.target.matrix.setRotateY(math.radians(30.))
                scene.target.matrix.translation = (0., 0., 100.)
                job = self.refresh(value, scene, runtime, bot)
                self.assertNotEqual(old, policy._stamp(policy.frame, job[1], job[2]))
                self.assertIsNone(policy._current(job))
                with mock.patch.object(policy.evaluator, '_armour_geometry',
                                       wraps=policy.evaluator._armour_geometry) as armour:
                    for unused in range(8):
                        row = policy._evaluate(job, scene.now, 'foreground')
                        if row['armor'] in ('passed', 'failed'):
                            break
                        job = self.refresh(value, scene, runtime, bot)
                self.assertGreater(armour.call_count, 0)
                anchor = policy.evaluator.review.targets[job[0][1]]['anchor']
                other = self.refresh(value, scene, runtime, bot, sample=1)
                policy._evaluate(other, scene.now, 'foreground')
                self.assertEqual(anchor, policy.evaluator.review.targets[job[0][1]]['anchor'])

    def test_cached_point_enumeration_cannot_expand_the_trajectory_work_budget(self):
        for bot in (False, True):
            with self.subTest(bot=bot), contextlib.redirect_stdout(io.StringIO()):
                value, scene, runtime = self.fixture(bot)
                policy, evaluator = runtime.attack_policy, runtime.attack_policy.evaluator
                # Populate the finite native sample set before ordinary motion.
                jobs = policy._jobs(shell_index=runtime.gun.shot_index)
                evaluator._budgets['foreground'] = 10000
                for job in jobs:
                    policy._evaluate(job, scene.now, 'foreground')
                scene.pose(scene.target, (1., 0., 101.))
                self.refresh(value, scene, runtime, bot)
                policy._used['foreground'] = 0
                with mock.patch.object(evaluator, '_prediction', wraps=evaluator._prediction) as prediction:
                    policy._rows_for('penetration', runtime.gun.shot_index, fresh_line=True)
                    self.assertEqual(0, prediction.call_count,
                        'reading retained rows must not calculate every trajectory outside the frontier')
                module = native.ADMISSION.rsplit('.', 1)[0]+'.attack_policy'
                with mock.patch(module+'.ballistics.ballistic_intercept',
                                wraps=__import__(module, fromlist=['ballistics']).ballistics.ballistic_intercept) as solve:
                    policy._frontier(scene.now, accepts=lambda row: False)
                    self.assertLessEqual(solve.call_count, policy.foreground_budget)
                self.assertLessEqual(policy._used['foreground'], policy.foreground_budget)

    def test_forward_motion_and_own_lateral_motion_use_the_vehicle_centre_line(self):
        for bot in (False, True):
            with self.subTest(bot=bot), contextlib.redirect_stdout(io.StringIO()):
                value, scene, runtime = self.fixture(bot)
                old = value.candidate['pose_stamp']
                scene.pose(scene.target, (0., 0., 150.))
                job = self.refresh(value, scene, runtime, bot)
                policy = runtime.attack_policy
                self.assertEqual(old, policy._stamp(policy.frame, job[1], job[2]))
                x = -150. * math.tan(math.radians(30.))
                if bot:
                    value.state['x'] = x
                else:
                    scene.battle.local_pose = lambda: ((x, 0., 0.), scene.body.yaw)
                job = self.refresh(value, scene, runtime, bot)
                self.assertNotEqual(old, policy._stamp(policy.frame, job[1], job[2]))
                self.assertEqual(('centre_line',),
                    policy.frame['review_reasons'][job[0][1]]['changed'])

    def test_vehicle_review_diagnostics_require_the_detailed_log_option(self):
        for enabled in (False, True):
            with self.subTest(detailed=enabled), contextlib.redirect_stdout(io.StringIO()):
                value, scene, runtime = self.fixture()
                scene.target.matrix.setRotateY(math.radians(30.))
                scene.target.matrix.translation = tuple(scene.target.position)
                module = native.ADMISSION.rsplit('.', 1)[0]+'.attack_policy'
                with mock.patch(module+'.combat_detail_enabled', return_value=enabled), \
                        mock.patch(module+'.combat_detail') as detail:
                    self.refresh(value, scene, runtime, False)
                events = [call for call in detail.call_args_list
                          if call.args[1] == 'vehicle_armour_review']
                self.assertEqual(int(enabled), len(events))
                if enabled:
                    self.assertEqual(30., events[0].args[-1]()['threshold_degrees'])

    def test_he_fallback_scores_surface_without_reopening_the_same_plate_trial(self):
        with contextlib.redirect_stdout(io.StringIO()):
            value, scene, runtime = self.fixture()
            scene.set_he(piercing=30.)
            for name in ('chassis', 'hull', 'turret', 'gun'):
                getattr(scene.target.typeDescriptor, name).materials[0].armor = 10000.
            scene.lay(mode='penetration')
            self.assertEqual('failed', scene.candidate['armor'])
            scene.body.setRotateYPR((.05, 0., 0.))
            for name in ('chassis', 'hull', 'turret', 'gun'):
                getattr(scene.target.typeDescriptor, name).materials[0].armor = 1.
            with mock.patch(native.ADMISSION+'.combat_rules.resolve_armor_contact',
                            side_effect=AssertionError('fallback repeated the plate trial')):
                scene.lay(mode='he_fallback')
            self.assertEqual('failed', scene.candidate['armor'])
            self.assertTrue(scene.candidate['contact'])

    def test_unrelated_turret_animation_during_launch_cannot_revoke_player_or_bot(self):
        for bot in (False, True):
            with self.subTest(bot=bot), contextlib.redirect_stdout(io.StringIO()):
                value, scene, runtime = self.fixture(bot)
                other = scene.vehicle(44, (120., 0., 200.), 2)
                self.observe_other(value, scene, runtime, other, bot)
                if bot:
                    original = runtime.gun.native.begin_burst
                    def changed(*args):
                        result = original(*args)
                        other.appearance.turretMatrix.setRotateY(.2)
                        return result
                    target, name = runtime.gun.native, 'begin_burst'
                else:
                    original = scene.battle._preinstall_player_projectile
                    def changed(*args):
                        result = original(*args)
                        other.appearance.turretMatrix.setRotateY(.2)
                        return result
                    target, name = scene.battle, '_preinstall_player_projectile'
                with mock.patch.object(target, name, changed):
                    self.assertTrue(value.fire())
                self.assertEqual([19, 10], runtime.gun.ammo)

    def test_new_intervening_vehicle_during_launch_still_revokes_geometric_proof(self):
        for bot in (False, True):
            with self.subTest(bot=bot), contextlib.redirect_stdout(io.StringIO()):
                value, scene, runtime = self.fixture(bot)
                other = scene.vehicle(44, (120., 0., 50.), 2)
                self.observe_other(value, scene, runtime, other, bot)
                if bot:
                    original = runtime.gun.native.begin_burst
                    target, name = runtime.gun.native, 'begin_burst'
                else:
                    original = scene.battle._preinstall_player_projectile
                    target, name = scene.battle, '_preinstall_player_projectile'
                def changed(*args):
                    result = original(*args)
                    scene.pose(other, (0., 0., 50.))
                    return result
                with mock.patch.object(target, name, changed):
                    self.assertFalse(value.fire())
                self.assertEqual([20, 10], runtime.gun.ammo)

    def test_cleared_front_point_recovers_without_repeating_armour_or_stealing_aim(self):
        with contextlib.redirect_stdout(io.StringIO()):
            value, scene, runtime = self.fixture()
            front = scene.vehicle(43, (0., 0., 50.), 2)
            self.assertFalse(scene.fire())
            policy = runtime.attack_policy
            key = scene.candidate['key']
            self.assertIn(key, policy._admission_blocks)
            scene.pose(front, (20., 0., 50.))
            job = self.refresh(value, scene, runtime, False)
            selected = (key[0], key[1], 1, key[3])
            policy.selected = selected
            with mock.patch.object(policy.evaluator, '_armour_geometry',
                                   side_effect=AssertionError('clearance is geometry only')):
                for unused in range(8):
                    row = policy._evaluate(job, scene.now, 'foreground')
                    if row['line'] == 'clear':
                        break
                    job = self.refresh(value, scene, runtime, False)
            self.assertEqual('clear', row['line'])
            self.assertEqual('passed', row['armor'])
            self.assertNotIn(key, policy._admission_blocks)
            self.assertEqual(selected, policy.selected)


if __name__ == '__main__':
    unittest.main()
