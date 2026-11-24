"""Crew retraining keeps the retail role-level losses of each school."""

import copy
import unittest
from unittest import mock

import test_port_0922_garage as fixture


def respecialize_level(role_level, same_vehicle, same_class, school):
    """#1513 items.tankmen.TankmanDescr.respecialize, lines 778-784.

    roleLevelLoss = 0 for the same vehicle, else baseRoleLoss; plus
    classChangeRoleLoss for another vehicle class; then
    max(school roleLevel, int(round(roleLevel * (1 - roleLevelLoss)))).
    """
    loss = 0.0 if same_vehicle else school['baseRoleLoss']
    if not same_class:
        loss += school['classChangeRoleLoss']
    return max(school['roleLevel'], int(round(role_level * (1.0 - loss))))


class RetrainingLossTests(unittest.TestCase):

    def setUp(self):
        self.economy = fixture._load('economy')
        self.data = fixture._load('data')

    def tables(self):
        return (('career', self.economy.CAREER_TANKMAN_COSTS),
                ('sandbox', self.economy.SANDBOX_TANKMAN_COSTS),
                ('fallback', self.data.DEFAULT_TANKMAN_COSTS))

    def test_each_school_loses_the_retail_share_for_the_same_class(self):
        for name, schools in self.tables():
            with self.subTest(table=name):
                self.assertEqual(
                    [80, 90, 100],
                    [respecialize_level(100, False, True, school)
                     for school in schools])

    def test_another_class_adds_the_class_change_loss(self):
        for name, schools in self.tables():
            with self.subTest(table=name):
                self.assertEqual(
                    [60, 80, 100],
                    [respecialize_level(100, False, False, school)
                     for school in schools])

    def test_the_school_minimum_still_floors_a_weak_crew_member(self):
        for name, schools in self.tables():
            with self.subTest(table=name):
                self.assertEqual(
                    [50, 75, 100],
                    [respecialize_level(60, False, False, school)
                     for school in schools])

    def test_the_current_vehicle_costs_no_level(self):
        for name, schools in self.tables():
            with self.subTest(table=name):
                self.assertEqual(
                    [100, 100, 100],
                    [respecialize_level(100, True, True, school)
                     for school in schools])

    def test_sandbox_changes_only_the_price(self):
        keys = ('roleLevel', 'baseRoleLoss', 'classChangeRoleLoss', 'isPremium')
        for career, sandbox in zip(self.economy.CAREER_TANKMAN_COSTS,
                                   self.economy.SANDBOX_TANKMAN_COSTS):
            self.assertEqual([career[key] for key in keys],
                             [sandbox[key] for key in keys])
            self.assertEqual((0, 0), (sandbox['credits'], sandbox['gold']))

    def test_the_garage_forwards_the_chosen_school_losses_to_the_client(self):
        unused, unused, garage = fixture._request_modules()
        economy = fixture._load('economy')
        snapshot = copy.deepcopy(fixture.SNAPSHOT)
        snapshot['tankmanCosts'] = economy.CAREER_TANKMAN_COSTS
        snapshot['unlockItemCompactDescrs'] = {50001, 50002}
        snapshot['wallet'] = {'credits': 100000, 'gold': 1000, 'freeXP': 0}
        vehicles, tankmen = fixture._modules()
        state = garage.GarageState(
            snapshot, vehicles_module=vehicles, tankmen_module=tankmen)
        calls = []
        original = tankmen.TankmanDescr.respecialize

        def spy(descriptor, *args):
            calls.append(args)
            return original(descriptor, *args)

        with mock.patch.object(tankmen.TankmanDescr, 'respecialize', spy):
            for school in range(3):
                state.retrain_tankman(101, school, 50002)

        self.assertEqual(
            [(2, 50, 0.2, 0.2, False), (2, 75, 0.1, 0.1, False),
             (2, 100, 0.0, 0.0, True)], calls)


if __name__ == '__main__':
    unittest.main()
