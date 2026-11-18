"""Actor entry parity and finite review work; native observations are fixtures.

These checks do not claim Windows physics or frame-pacing acceptance.
"""
import copy
import math
from types import SimpleNamespace
import unittest

from test_player_rebuilt_attack_policy import Observations, AttackPolicy
from test_player_combat_ownership import OwnershipScene
from test_player_siege_engagement import SiegeScene
from test_player_fire_admission_complete import SpatialPose, f
from test_port_0922_bot_state_codec import _bot_state, STATIC
from gui.mods.offline_lan_0922 import hull_aiming, shot_geometry, bot_state_codec
from gui.mods.offline_lan_0922.vehicle_control.bot_binding import BotControlBinding
from gui.mods.offline_lan_0922.vehicle_control.combat_stop import CombatStop
from gui.mods.offline_lan_0922.vehicle_control.native_aim import active_hydraulic_pose
from gui.mods.offline_lan_0922.entities.native_remote_vehicle import _NativeRemoteState


def descriptor():
    pitch = dict(isAvailable=True, isEnabled=True,
        wheelsCorrectionAngles=dict(pitchMin=-.4, pitchMax=.4),
        wheelsCorrectionSpeed=.3, wheelCorrectionCenterZ=1.5)
    return SimpleNamespace(hasSiegeMode=True, gun=SimpleNamespace(),
        type=SimpleNamespace(hullAimingParams=dict(pitch=pitch)))


class ActorEntryParityTests(unittest.TestCase):
    def binding_policy(self, kind):
        if kind == 'bot':
            # This checks the production binding constructor without claiming
            # to create a native motion simulation in the analytic fixture.
            engine = SimpleNamespace(round_id=7, states={11: dict(id=11,
                x=0., y=0., z=0., fire_seq=0)}, _ammo_states={})
            battle = SimpleNamespace(_generation=7, _last_frame_time=0.)
            return BotControlBinding(battle, engine, 11).attack_policy
        scene = SiegeScene() if kind == 'siege_player' else OwnershipScene()
        scene.setUp()
        self.addCleanup(scene.doCleanups)
        scene.configure()
        return scene.runtime.attack_policy

    def observations(self, policy, **options):
        options.setdefault('he_validation', 'single_point')
        scene = Observations(**options)
        original = policy.runtime, policy.evaluator
        self.addCleanup(setattr, policy, 'runtime', original[0])
        self.addCleanup(setattr, policy, 'evaluator', original[1])
        # Preserve the policy installed by the real binding. Supply only
        # factual finite geometry at its observation seam, not new flags.
        policy.reset()
        policy.runtime, policy.evaluator = SimpleNamespace(), scene
        scene.policy = policy
        scene.frame['ordered'] = policy.ordered_load(scene.frame) is not None
        return scene

    def test_real_actor_entries_finish_current_vehicle_before_cached_other(self):
        for kind in ('player', 'siege_player', 'bot'):
            with self.subTest(kind=kind):
                scene = self.observations(self.binding_policy(kind), targets=2, points=3)
                scene.passed(0, 1, 2)
                scene.passed(0, 2, 0)
                policy = scene.policy
                policy.frame = scene.snapshot(0.)
                job = next(job for job in policy._jobs(shell_index=0)
                           if job[0][1] == ('bot', 2) and job[3] == 0)
                policy._evaluate(job, 0., 'background')
                result = scene.tick(0., background=False)
                self.assertEqual((0, ('bot', 1), 2, 'penetration'), result['candidate']['key'])

    def test_real_actor_entries_use_higher_penetration_before_he(self):
        for kind in ('player', 'siege_player', 'bot'):
            with self.subTest(kind=kind):
                scene = self.observations(self.binding_policy(kind), targets=1, points=1)
                scene.passed(1)
                scene.passed(2)
                scene.prime()
                result = scene.tick(0., background=False)
                self.assertEqual(1, result['shell_index'])
                self.assertEqual('ordered_penetration_exhausted', result['reason'])

    def test_real_actor_entries_count_two_higher_penetration_commits(self):
        for kind in ('player', 'siege_player', 'bot'):
            with self.subTest(kind=kind):
                scene = self.observations(self.binding_policy(kind), targets=1, points=1, he=False)
                scene.frame['loaded'] = 1
                scene.passed(0)
                scene.passed(1)
                scene.tick(0., background=False)
                scene.prime()
                candidate = dict(shell_index=1, mode='penetration',
                    key=(1, ('bot', 1), 0, 'penetration'))
                self.assertEqual((None, 'keep_mounted_shell'),
                                 scene.policy.next_at_edge(trigger=candidate))
                scene.policy.shot_committed(dict(shell_index=1),
                    dict(player_control=dict(automatic=True, candidate=candidate)))
                plan, reason = scene.policy.next_at_edge(trigger=candidate)
                self.assertEqual(0, plan['shell_index'])
                self.assertEqual('higher_penetration_cycle_finished', reason)
                self.assertTrue(plan['trigger_only'])


class AdmissionParityTests(unittest.TestCase):
    def owner(self, actor, siege=False):
        target = dict(kind='bot', id=29, network_id=29, alive=True, health=500,
            position=(-26., 2., 438.), visible=True, ready=True)
        state = dict(position=(-20., 3., 400.), x=-20., y=3., z=400., yaw=0.,
            profile=dict(class_tag='LT'), siege_state=0)
        runtime = SimpleNamespace(state=state, now=10., actor_kind=actor,
            features={'drive', 'fire'}, gun=SimpleNamespace(shot_index=0),
            siege_capable=lambda: siege, _mission=None, _mission_brakes=lambda: False,
            _native_hull_laying=None, visible_targets=lambda: (target,))
        owner = CombatStop(runtime)
        runtime.combat_stop = owner
        return owner

    def test_every_moving_actor_confirms_and_can_review_capture_approach(self):
        for actor in ('human', 'bot'):
            for siege in (False, True):
                with self.subTest(actor=actor, siege=siege):
                    owner = self.owner(actor, siege)
                    area = dict(point=dict(x=0., y=0., z=410.), radius=50.)
                    order = dict(combat_mode='route', throttle_override=None,
                        move_position=(0., 0., 410.))
                    owner.accept(order)
                    self.assertTrue(owner._route_requires_confirmation(order))
                    order.update(combat_mode='base_capture', capture_objective=area)
                    owner.accept(order)
                    self.assertTrue(owner.active)
                    self.assertTrue(owner.can_request_movement)
                    order.update(throttle_override=0., capture_area=area)
                    owner.accept(order)
                    self.assertTrue(owner.capture_hold())
                    self.assertFalse(owner.can_request_movement)


class BlockedReviewProgressTests(unittest.TestCase):
    def scene(self):
        scene = Observations(targets=3, points=9, he_validation='single_point')
        scene.policy = AttackPolicy(SimpleNamespace(), evaluator=scene, ordered=True)
        scene.frame.update(loaded=2, ordered=True)
        for target in (1, 2, 3):
            for sample in range(9):
                scene.value(2, target, sample, line='world_blocked', armor='unknown')
        return scene

    def test_moving_source_visits_other_target_without_spare_budget(self):
        scene = self.scene()
        for sample in range(9):
            scene.passed(2, 2, sample)
        result = scene.tick(0.)
        self.assertEqual('wait', result['action'])
        self.assertEqual([('bot', 2), ('bot', 3), ('bot', 1)], scene.policy.ordered.order)
        scene.frame.update(pose=('source', 1), position=(4., 0., 0.))
        result = scene.tick(.1)
        self.assertEqual(('bot', 2), result['candidate']['target_key'])
        self.assertEqual('aim', result['action'])
        self.assertEqual(2, scene.policy.foreground_budget)

    def test_all_blocked_targets_get_one_final_revisit_then_release(self):
        scene = self.scene()
        seen = []
        for step in range(15):
            scene.frame.update(pose=('source', step), position=(step * 3., 0., 0.))
            before = len(scene.calls)
            result = scene.tick(step * 2.1)
            calls = scene.calls[before:]
            if calls:
                seen.append(calls[0][3])
            if result['action'] == 'navigate':
                break
        self.assertEqual('navigate', result['action'])
        self.assertEqual([('bot', 1), ('bot', 2), ('bot', 3), ('bot', 1)], seen)
        self.assertFalse(scene.policy.selected)

    def test_moving_source_finishes_blocked_inspection_without_any_atomic_slice(self):
        scene = self.scene()
        scene.allow_atomic = False
        for sample in range(9):
            scene.passed(2, 2, sample)
        queried = set()
        for step in range(12):
            scene.frame.update(pose=('source', step), position=(step * 4., 0., 0.))
            before = len(scene.calls)
            result = scene.tick(step * .1)
            queried.update(call[4] for call in scene.calls[before:] if call[3] == ('bot', 1))
            if result['action'] == 'aim':
                break
        self.assertEqual(set(range(9)), queried)
        self.assertEqual(('bot', 2), result['candidate']['target_key'])
        self.assertEqual('clear', result['candidate']['line'])
        self.assertEqual(scene.frame['pose'], result['candidate']['solution']['source_pose'])
        self.assertFalse(any(call[1] == 'atomic' for call in scene.calls))


class HydraulicPoseParityTests(unittest.TestCase):
    def test_worker_body_and_shared_review_agree_on_report_cross_slope(self):
        state = dict(id=24, x=449.7328, y=10.4051, z=204.6935,
            yaw=2.5479157524385916, terrain_pitch=-.281933321888457,
            pitch=-.04029245232874787, roll=-.18880275816067352,
            suspension_pitch=.24164086955970913, turret_yaw=0., gun_pitch=0., siege_state=2)
        state['position'] = tuple(state[axis] for axis in ('x', 'y', 'z'))
        original = copy.deepcopy(state)
        installed = descriptor()
        entity = SimpleNamespace(typeDescriptor=installed, siegeState=2)
        binding = BotControlBinding.__new__(BotControlBinding)
        binding.actor_id, binding.physical = 24, binding
        binding.engine = SimpleNamespace(states={24: state}, _terrain_pitch=lambda value: value['terrain_pitch'])
        binding.owner = SimpleNamespace(_runtime=SimpleNamespace(math=SimpleNamespace(Matrix=SpatialPose)),
                                       _vector=f._Vector)
        binding.source_entity = lambda: entity
        binding.source_descriptor = lambda: installed
        pose = binding.source_pose(origin=(0., 0., 0.))
        frame = dict(descriptor=installed, pose=pose, body=pose[1])
        hydraulic = active_hydraulic_pose(binding, frame)
        self.assertIsNotNone(hydraulic)
        self.assertGreater(abs(pose[1][0] - state['yaw']), .04)
        self.assertEqual(original, state)

    def test_native_presentation_uses_same_local_pivot_and_keeps_ground(self):
        native = _NativeRemoteState.__new__(_NativeRemoteState)
        native.entity = SimpleNamespace(typeDescriptor=descriptor(), siegeState=2,
                                        model=SimpleNamespace(matrix=None))
        native._math = SimpleNamespace(Matrix=SpatialPose, MatrixProduct=f._MatrixProduct, Vector3=f._Vector)
        native.matrix = SpatialPose()
        native.matrix.setRotateYPR((.4, .13, -.17))
        native.matrix.translation = f._Vector(1., 2., 3.)
        native.provider = native.matrix
        native.position = f._Vector(1., 2., 3.)
        native.yaw, native.speed, native.turn_speed = .4, 0., 0.
        native.velocity = native.acceleration = f._Vector()
        native._authority_geometry = False
        native._canonical_hydraulic_matrix = native._canonical_hydraulic_provider = None
        native._siege_relative_body_matrix = native._siege_body_matrix = None
        native._compatibility = SimpleNamespace(set_vehicle_pose_overlay=lambda *a, **k: None)
        self.assertTrue(native.set_hydraulic_pitch(-.12))
        body, ground = native.collision_matrices()
        self.assertIs(native.matrix, ground)
        actual = SpatialPose(body.b)
        actual.preMultiply(body.a)
        mounted, angles = hull_aiming.compose_body((1., 2., 3.), (.4, .13, -.17), -.12, 1.5)
        for local in ((0., 0., 0.), (0., 0., 1.), (1., .8, -2.)):
            expected = shot_geometry.transform_vehicle_point(local, mounted, *angles)
            for left, right in zip(actual.applyPoint(f._Vector(local)), expected):
                self.assertAlmostEqual(left, right, places=9)

    def test_hydraulic_input_survives_the_real_bot_wire_codec(self):
        state = _bot_state(suspension_pitch=.24164086955970913)
        decoded = bot_state_codec.decode_row(bot_state_codec.encode_row(state), STATIC)
        self.assertAlmostEqual(.24164, decoded['suspension_pitch'], places=5)


if __name__ == '__main__':
    unittest.main()
