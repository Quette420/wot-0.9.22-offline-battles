"""Equipment effects must reach damage/perception, not just the fitting UI."""
import contextlib
import io
import types
import unittest
from unittest import mock

import test_port_0922_critical_damage as critical_fixture
from test_port_0922_server_projectiles import _state, _update_player_input
from gui.mods.offline_lan_0922 import bot_fittings, bot_runtime, crew_battle
from gui.mods.offline_lan_0922 import critical_damage, device_damage, effective_params as wire
from gui.mods.offline_lan_0922 import environment_modules, loadout, player_critical_mechanics


class EquipmentSkillEffectsTests(unittest.TestCase):
    def test_liner_changes_the_real_crew_roll_for_shots_and_explosions(self):
        scene = critical_fixture.CriticalDamageTests()
        scene.setUp()
        for explosion in (False, True):
            for factor, injured in ((1.0, True), (0.8, True), (0.75, False),
                                    (0.7, False), (0.5, False)):
                descriptor = critical_fixture._descriptor()
                descriptor.miscAttrs['crewChanceToHitFactor'] = factor
                target = types.SimpleNamespace(id=999, health=500,
                    typeDescriptor=descriptor, position=object(), matrix=object(),
                    getComponents=lambda: ())
                collision = (1.0, 1.0, critical_fixture._Material(
                    'commanderHealth', chance=0.4), None)
                with mock.patch.dict('sys.modules', {'BigWorld': scene.bigworld, 'Math': scene.math}), \
                        mock.patch('random.uniform', return_value=5000.0), \
                        mock.patch('random.random', return_value=0.31) as roll, \
                        contextlib.redirect_stdout(io.StringIO()):
                    damage, payload, delta = critical_damage.propose_direct(
                        target, (collision,), object(), object(), 100,
                        {'kind': 'ARMOR_PIERCING', 'damage': (100, 5000)}, 2,
                        penetrated=True, by_explosion=explosion, with_delta=True)
                self.assertEqual(injured, 'commander' in delta['crew_ko'])
                roll.assert_called_once()

    def test_all_four_liners_preserve_native_crew_protection_in_player_handoff(self):
        for protection in (0.8, 0.75, 0.7, 0.5):
            descriptor = critical_fixture._strict_1513_descriptor()
            descriptor.miscAttrs.crewChanceToHitFactor = protection
            profile = player_critical_mechanics.project_profile(descriptor)
            canonical = wire._canonical_critical(profile)
            restored = player_critical_mechanics.descriptor_from_profile(canonical)
            self.assertEqual(protection, device_damage._misc_factor(
                restored, 'crewChanceToHitFactor'))

    def test_toolbox_repair_factor_survives_player_handoff(self):
        # The server rebuilds the player vehicle from this profile. Without
        # the factor its empty miscAttrs silently drop the toolbox for every
        # non-track module repair.
        for toolbox in (1.0, 1.25, 1.5):
            descriptor = critical_fixture._strict_1513_descriptor()
            descriptor.miscAttrs.repairSpeedFactor = toolbox
            canonical = wire._canonical_critical(
                player_critical_mechanics.project_profile(descriptor))
            restored = player_critical_mechanics.descriptor_from_profile(canonical)
            self.assertEqual(toolbox, device_damage._misc_factor(
                restored, 'repairSpeedFactor'))
            self.assertAlmostEqual(
                device_damage.repair_seconds('engineHealth', descriptor, repair_factor=1.0),
                device_damage.repair_seconds('engineHealth', restored, repair_factor=1.0))

    def test_player_repair_uses_current_crew_row_not_garage_constant(self):
        snapshot = {'loadout': {'repair_factor': 1.0}, 'crew': {'dynamic_spotting': {
            'crew': ['commander', 'driver'],
            'states': {'0:0': {'battle_factors': dict(crew_battle.DEFAULTS, repair_speed_factor=1.0)},
                       '2:0': {'battle_factors': dict(crew_battle.DEFAULTS, repair_speed_factor=0.6)}}}}}
        healthy = crew_battle.for_critical(snapshot, {'crew_ko': []})
        injured = crew_battle.for_critical(snapshot, {'crew_ko': ['driver']})
        self.assertEqual(1.0, healthy['repair_speed_factor'])
        self.assertEqual(0.6, injured['repair_speed_factor'])

    def test_protection_wire_rejects_invalid_values_and_does_not_alias(self):
        profile = player_critical_mechanics.project_profile(
            critical_fixture._strict_1513_descriptor())
        canonical = wire._canonical_critical(profile)
        profile['protection']['crewChanceToHitFactor'] = 0.5
        self.assertEqual(1.0, canonical['protection']['crewChanceToHitFactor'])
        for bad in (True, -0.1, 1.1, float('inf'), float('nan')):
            profile['protection']['crewChanceToHitFactor'] = bad
            self.assertIsNone(wire._canonical_critical(profile))

    def test_suspension_reduces_only_proved_track_transmitted_hull_loss(self):
        descriptor = critical_fixture._strict_1513_descriptor()
        descriptor.miscAttrs.vehicleByChassisDamageFactor = 0.5
        for name in ('leftTrackHealth', 'rightTrackHealth'):
            self.assertEqual(150, environment_modules.suspension_hull_damage(
                300, descriptor, [dict(name=name, weight=1.0)], (0, 1, 0)))
        for contacts in ([], [dict(name='gunHealth', weight=1.0)],
                         [dict(name='engineHealth', weight=1.0)]):
            self.assertEqual(300, environment_modules.suspension_hull_damage(
                300, descriptor, contacts, (0, 1, 0)))
        for normal in (None, (0, -1, 0), (1, 0, 0)):
            self.assertEqual(300, environment_modules.suspension_hull_damage(
                300, descriptor, [dict(name='leftTrackHealth', weight=1.0)], normal))

    def test_server_landing_uses_installed_suspension_once_and_deduplicates(self):
        state = _state()
        player = state.players[1]
        descriptor = critical_fixture._strict_1513_descriptor()
        descriptor.miscAttrs.vehicleByChassisDamageFactor = 0.5
        player.effective_params['critical'] = player_critical_mechanics.project_profile(descriptor)
        self.assertTrue(_update_player_input(state, 1, up_cosine=1.0))
        message = dict(type='landing_observation', round_id=1,
            authority_epoch=state.authority_epoch, observation_seq=1,
            input_seq=player.input_seq, impact_speed=20.0,
            contact_normal=[0, 1, 0],
            module_contacts=[dict(name='leftTrackHealth', weight=1.0)])
        before = player.health
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(state.submit_landing_observation(1, message))
        expected = int(round(player.max_health * 0.3 * 0.5))
        self.assertEqual(expected, before - player.health)
        hp = player.health
        state.submit_landing_observation(1, message)
        self.assertEqual(hp, player.health)

    def test_recon_uses_native_destroyed_coefficient_without_double_normal_bonus(self):
        original = mock.Mock()
        crew = types.SimpleNamespace(_skillProcessors={'commander_eagleEye': original})
        factors = loadout._collect_battle_crew_factors(crew)
        config = types.SimpleNamespace(distanceFactorPerLevelWhenDeviceWorking=0.0002,
                                      distanceFactorPerLevelWhenDeviceDestroyed=0.002)
        crew._skillProcessors['commander_eagleEye'](crew, 0, 100, 10, True, False, config)
        original.assert_called_once()
        ratio = crew_battle.from_native(factors)['damaged_optics_recon_ratio']
        self.assertAlmostEqual(1.22 / 1.022, ratio)
        descriptor = critical_fixture._strict_1513_descriptor()
        self.assertEqual(1.0, device_damage.module_stat_factor(
            {}, set(), descriptor, 'vision', damaged_optics_recon_ratio=ratio))
        self.assertAlmostEqual(0.25 * ratio, device_damage.module_stat_factor(
            {}, {'surveyingDeviceHealth'}, descriptor, 'vision',
            damaged_optics_recon_ratio=ratio))
        self.assertEqual(0.5, device_damage.module_stat_factor(
            {'surveyingDeviceHealth': 40}, set(), descriptor, 'vision',
            damaged_optics_recon_ratio=ratio))

    def test_injured_recon_does_not_donate_a_destroyed_optics_bonus(self):
        crew = types.SimpleNamespace(_skillProcessors={})
        factors = loadout._collect_battle_crew_factors(crew)
        crew._skillProcessors['commander_eagleEye'](
            crew, 0, 100, 0, False, False, types.SimpleNamespace())
        self.assertEqual(1.0, crew_battle.from_native(factors)['damaged_optics_recon_ratio'])

    def test_fire_directive_factor_survives_wire_without_claiming_a_retail_burn_law(self):
        factors = crew_battle.from_native({'healthBurnPerSecLossFraction': 1.215})
        self.assertEqual(1.215, crew_battle.canonical(factors)['fire_decay_factor'])
        target = types.SimpleNamespace(typeDescriptor=critical_fixture._strict_1513_descriptor(),
                                       id=1, actor_kind='player')
        with mock.patch('gui.mods.offline_lan_0922.native_input_diagnostics.validation_event') as emit:
            critical_damage.report_fire_model(target, factors['fire_decay_factor'])
        data = emit.call_args.kwargs
        self.assertTrue(data['skill_applied'])
        self.assertIsNone(data['native_health_burn_per_second'])
        self.assertEqual(1.215, data['native_decay_factor'])

    def test_fire_diagnostic_missing_target_never_enters_native_player_lookup(self):
        with mock.patch.object(critical_damage, '_device_td', side_effect=AssertionError('native lookup')), \
                mock.patch('gui.mods.offline_lan_0922.native_input_diagnostics.validation_event') as emit:
            critical_damage.report_fire_model(types.SimpleNamespace(), 0.57)
        self.assertIsNone(emit.call_args.kwargs['native_health_burn_per_second'])


if __name__ == '__main__':
    unittest.main()
