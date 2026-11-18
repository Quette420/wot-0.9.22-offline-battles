"""One server parking owner across native player and worker connections."""
import copy
from pathlib import Path
import sys
import threading
from types import SimpleNamespace
import unittest

sys.path[:0] = [str(Path(__file__).resolve().parents[1]/'server'),
               str(Path(__file__).resolve().parents[1]/'src/res/scripts/client')]
from gui.mods.offline_lan_0922 import spg_reservations as reservations
from lan_battle_server import BattleState
from test_port_0922_spg_initial_positions import _graph, _states, positions


class SharedReservationsTests(unittest.TestCase):
    def setUp(self):
        self.state = object.__new__(BattleState)
        self.state.lock = threading.RLock()
        self.state.round_id, self.state.phase = 2, 'battle'
        self.state.bot_authority_id, self.state.authority_epoch = 99, 3
        self.state.map_name, self.state.bot_tactics = '08_ruinberg', None
        graph = _graph()
        plans, unused = positions.assign_initial_positions('08_ruinberg', graph, _states(graph))
        self.plan = plans[10]
        self.team = 1
        self.state.players = {1: SimpleNamespace(connected=True, alive=True,
            team=self.team, vehicle=self.plan['vehicle'])}
        self.state.bot_states = {12:dict(alive=True, health=100, team=self.team,
                                        vehicle=self.plan['vehicle'])}
        self.state._vehicle_is_spg = lambda vehicle: vehicle == self.plan['vehicle']

    def packet(self, kind, actor, plan, seq=1):
        return dict(type='spg_parking_request', round_id=2, seq=seq,
            actor_kind=kind, actor_id=actor, plan=plan,
            action='claim' if plan else 'release', authority_epoch=3)

    def test_player_and_worker_cannot_both_reserve_the_same_region(self):
        player = self.state.update_spg_parking(1, self.packet('human',1,self.plan))
        bot = self.state.update_spg_parking(99, self.packet('bot',12,self.plan))
        self.assertTrue(player['accepted'])
        self.assertFalse(bot['accepted'])
        self.assertEqual([dict(kind='human',id=1,team=self.team,zone=self.plan['zone'])],
                         bot['spg_parking']['claims'])

    def test_bot_first_grant_also_excludes_the_player(self):
        self.assertTrue(self.state.update_spg_parking(99,self.packet('bot',12,self.plan))['accepted'])
        self.assertFalse(self.state.update_spg_parking(1,self.packet('human',1,self.plan))['accepted'])
        self.state.bot_states[12]['alive'] = False
        self.assertTrue(self.state.update_spg_parking(1,self.packet('human',1,self.plan,2))['accepted'])

    def test_another_player_or_stale_worker_cannot_change_a_claim(self):
        self.assertFalse(self.state.update_spg_parking(7,self.packet('human',1,self.plan))['accepted'])
        packet=self.packet('bot',12,self.plan);packet['authority_epoch']=2
        self.assertFalse(self.state.update_spg_parking(99,packet)['accepted'])
        self.assertEqual([],self.state._spg_parking_book().snapshot()['claims'])

    def test_rejected_transfer_preserves_the_current_region(self):
        book=reservations.Registry(2)
        self.assertTrue(book.claim(('human',1),1,dict(zone='a')))
        self.assertTrue(book.claim(('bot',12),1,dict(zone='b')))
        self.assertFalse(book.claim(('human',1),1,dict(zone='b')))
        self.assertEqual('a',book.claims[('human',1)]['zone'])

    def test_release_supersedes_an_unacknowledged_claim_and_late_ack(self):
        sent=[]
        client=reservations.Client(lambda packet:sent.append(packet) or True,lambda:1.)
        client.observe(dict(round_id=2,revision=0,claims=[]))
        self.assertEqual('pending',client.request(('human',1),self.team,self.plan))
        self.assertEqual('pending',client.request(('human',1),self.team,None))
        self.assertEqual(['claim','release'],[p['action'] for p in sent])
        acknowledgements=[self.state.update_spg_parking(1,p) for p in sent]
        self.assertTrue(client.acknowledge(acknowledgements[1]))
        self.assertFalse(client.acknowledge(acknowledgements[0]))
        self.assertEqual((),client.claims)
        self.assertEqual([],self.state._spg_parking_book().snapshot()['claims'])

    def test_client_excludes_other_owners_and_retries_only_after_a_change(self):
        sent=[]; clock=[1.]
        client=reservations.Client(lambda p:sent.append(p) or True,lambda:clock[0])
        client.observe(dict(round_id=2,revision=0,claims=[]))
        client.request(('human',1),self.team,self.plan)
        ack=self.state.update_spg_parking(1,sent[0]);client.acknowledge(ack)
        self.assertEqual('granted',client.request(('human',1),self.team,self.plan))
        self.assertEqual([self.plan['zone']],client.excluded(('bot',12),self.team))
        self.assertEqual(1,len(sent))


if __name__ == '__main__':unittest.main()
