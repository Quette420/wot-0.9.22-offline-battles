"""Reviewed premium HE is primary penetration ammunition on every actor."""
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from test_player_rebuilt_attack_policy import Observations
import test_shared_pr119_live_report as report_fixtures
from gui.mods.offline_lan_0922.vehicle_control import ammunition_validation as roles
from gui.mods.offline_lan_0922.vehicle_control.attack_policy import AttackPolicy
from gui.mods.offline_lan_0922.bot_runtime import _BotAmmoState
from gui.mods.offline_lan_0922 import mobile_combat_test


class PrimaryHERulesTests(unittest.TestCase):
    def scene(self):
        scene = Observations(targets=2, points=2, he_validation='full')
        scene.policy = AttackPolicy(SimpleNamespace(), evaluator=scene, ordered=True)
        ap, ordinary, hesh = scene.frame['shells']
        ap['piercing'] = 260.
        ordinary.update(is_he=True, piercing=70., validation_mode=roles.SINGLE_POINT,
            gun_identity='uk:_5_5inch_AT_Gun', shell_identity='uk:_5_5inch_HE_Mk_1T')
        hesh.update(piercing=200., gun_identity='uk:_5_5inch_AT_Gun',
                    shell_identity='uk:_5_5inch_HESH_Mk_1')
        return scene

    def test_each_reviewed_pair_sweeps_other_cars_before_he_fallback(self):
        for gun, shell in roles.FULL_VALIDATION_HE:
            with self.subTest(gun=gun):
                scene = self.scene()
                scene.frame['loaded'] = 2
                scene.frame['shells'][2].update(gun_identity=gun, shell_identity=shell)
                scene.passed(2, target=2, sample=1)
                scene.he(500., target=1)
                for step in range(10):
                    result = scene.tick(step*.1)
                    if result['action']=='aim':break
                self.assertEqual((2, ('bot', 2), 1, 'penetration'), result['candidate']['key'])
                self.assertFalse(any(call[-1] == 'he_fallback' for call in scene.calls))

    def test_high_penetration_return_targets_primary_hesh_not_ordinary_he(self):
        scene = self.scene()
        scene.passed(0)
        result = scene.tick(0.)
        self.assertIsNone(scene.policy.next_at_edge(trigger=result['candidate'])[0])
        scene.policy.shot_committed(dict(shell_index=0), {})
        scene.tick(.1)
        plan, reason = scene.policy.next_at_edge(trigger=scene.policy.decision['candidate'])
        self.assertEqual(2, plan['shell_index'])
        self.assertEqual('higher_penetration_cycle_finished', reason)

    def test_primary_hesh_penetration_has_no_fallback_two_shot_limit(self):
        scene = self.scene()
        scene.frame['loaded'] = 2
        scene.passed(2)
        for step in range(6):
            result = scene.tick(step * .1)
            self.assertEqual('penetration', result['candidate']['mode'])
            scene.policy.shot_committed(dict(shell_index=2), {})
            self.assertEqual((None, 'keep_mounted_shell'),
                             scene.policy.ordered.next_load(scene.policy, result['candidate']))

    def test_gold_he_can_still_fallback_after_the_whole_penetration_sequence(self):
        scene = self.scene()
        scene.frame.update(loaded=2, ammo=(10, 10, 10))
        for step in range(10):
            result=scene.tick(step*.1)
            if result['action']=='switch_shell':break
        self.assertEqual(0, result['shell_index'])
        scene.frame['loaded'] = 0
        for step in range(10):
            result=scene.tick(1.+step*.1)
            if result['action']=='switch_shell':break
        self.assertEqual(('ordered_he_fallback_load', 2), (result['reason'], result['shell_index']))
        scene.frame['loaded'] = 2
        scene.he(100., target=scene.policy.ordered.target[1])
        result = scene.tick(2.)
        self.assertEqual('he_fallback', result['candidate']['mode'])

    def test_ordinary_he_fallback_remains_available_when_hesh_is_out_of_stock(self):
        scene = self.scene()
        scene.frame.update(loaded=0, ammo=(10, 10, 0))
        for step in range(10):
            result = scene.tick(step * .1)
            if result['action'] == 'switch_shell':
                break
        self.assertEqual(('ordered_he_fallback_load', 1),
                         (result['reason'], result['shell_index']))

    def test_equal_test_rack_keeps_all_shells_and_loads_the_reviewed_primary(self):
        vehicle = mobile_combat_test.CONWAY
        gun, rounds = mobile_combat_test.LOADOUTS[vehicle]
        shells=[dict(index=i, name=name, kind='ARMOR_PIERCING' if i==0 else 'HIGH_EXPLOSIVE')
                for i,(name,count) in enumerate(rounds)]
        profile=dict(vehicle_name=vehicle, gun_name=gun, class_tag='AT-SPG',
                     ammo_ratios=[1,1,1], shells=shells)
        descriptor=dict(gun=dict(name=gun,maxAmmo=30,shots=[dict(shell=s) for s in shells]))
        with patch.dict(os.environ, {mobile_combat_test.ENV:'1','WOT_OFFLINE_DIAGNOSTICS':'1'}):
            ammo=_BotAmmoState(descriptor,profile)
        self.assertEqual([10,10,10],ammo.remaining)
        self.assertEqual(1,ammo.loaded)

    def test_same_mounted_hesh_returns_to_penetration_role_after_real_fallbacks(self):
        scene=self.scene()
        scene.frame.update(loaded=2,ammo=(10,0,10))
        scene.policy.ordered.fallback_load=2
        scene.he(100.)
        for step in range(5):
            result=scene.tick(step*.1)
            if result['action']=='aim':break
        self.assertEqual('he_fallback',result['candidate']['mode'])
        for unused in range(2):scene.policy.ordered.shot_committed(2,'he_fallback')
        scene.frame['scene']+=1
        scene.passed(2)
        for step in range(5):
            result=scene.tick(1.+step*.1)
            if result['action']=='aim':break
        self.assertEqual('penetration',result['candidate']['mode'])
        self.assertIsNone(scene.policy.ordered.fallback_load)

    def test_finite_he_damage_comparison_survives_small_source_motion(self):
        scene=Observations(targets=2,points=5,he_validation='single_point')
        scene.policy=AttackPolicy(SimpleNamespace(),evaluator=scene,ordered=True)
        scene.frame['loaded']=2
        scene.allow_atomic=False
        for sample in range(5):scene.he(20.+sample*30.,sample=sample)
        scene.he(1000.,target=2)
        visited=set()
        for step in range(40):
            report_fixtures.ReportAmmunitionTests.pose(scene,step*.00001)
            result=scene.tick(step*.1)
            visited.update(call[4] for call in scene.calls if call[-1]=='he_fallback')
            if result['action']=='aim':break
        self.assertEqual(set(range(5)),visited)
        self.assertEqual((2,('bot',1),4,'he_fallback'),result['candidate']['key'])
        self.assertEqual(scene.frame['pose'],result['candidate']['solution']['source_pose'])
        self.assertEqual({('bot',1)},{call[3] for call in scene.calls})


if __name__=='__main__':unittest.main()
