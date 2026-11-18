"""Round-scoped parking claims shared by native players and the Bot worker.

Only the server grants a region. Clients retain their existing sourced-point
selection and movement; a rejected proposal never evicts the previous claim.
"""
import copy

try:
    TEXT = (basestring,)
    INTEGER = (int, long)
except NameError:
    TEXT, INTEGER = (str,), (int,)


class Registry(object):
    def __init__(self, round_id):
        self.round_id = round_id
        self.revision = 0
        self.claims = {}

    def claim(self, owner, team, plan):
        owner = tuple(owner)
        zone = str(plan['zone'])
        for key, row in self.claims.items():
            if key != owner and row['team'] == team and row['zone'] == zone:
                return False
        old = self.claims.get(owner)
        if old is None and sum(row['team'] == team for row in self.claims.values()) >= 3:
            return False
        if old is None or old['team'] != team or old['zone'] != zone:
            self.claims[owner] = dict(team=team, zone=zone)
            self.revision += 1
        return True

    def release(self, owner):
        if self.claims.pop(tuple(owner), None) is not None:
            self.revision += 1

    def prune(self, alive):
        for owner in list(self.claims):
            if not alive(owner):
                self.release(owner)

    def snapshot(self):
        return dict(round_id=self.round_id, revision=self.revision,
            claims=[dict(row, kind=owner[0], id=owner[1])
                    for owner, row in sorted(self.claims.items())])


class Client(object):
    def __init__(self, send, clock):
        self.send, self.clock = send, clock
        self.round_id = None
        self.revision = -1
        self.claims = ()
        self.sequence = 0
        self.requests = {}

    def observe(self, value):
        if not isinstance(value, dict):
            return False
        round_id, revision, rows = value.get('round_id'), value.get('revision'), value.get('claims')
        if (not isinstance(round_id, INTEGER) or not isinstance(revision, INTEGER) or
                revision < 0 or not isinstance(rows, list) or len(rows) > 30):
            return False
        if any(not isinstance(row, dict) or row.get('kind') not in ('human', 'bot') or
               not isinstance(row.get('id'), INTEGER) or row['id'] <= 0 or
               row.get('team') not in (1, 2) or not isinstance(row.get('zone'), TEXT) or
               not 1 <= len(row['zone']) <= 96 for row in rows):
            return False
        if round_id != self.round_id:
            self.round_id, self.revision, self.requests = round_id, -1, {}
        if revision < self.revision:
            return False
        self.revision, self.claims = revision, tuple(copy.deepcopy(rows))
        return True

    def acknowledge(self, message):
        value = message.get('spg_parking')
        if not self.observe(value):
            return False
        owner = message.get('actor_kind'), message.get('actor_id')
        request = self.requests.get(owner)
        if (request is None or message.get('seq') != request['seq'] or
                not isinstance(message.get('accepted'), bool)):
            return False
        request['result'] = ('granted' if message['accepted'] else
                             'pending' if message.get('code') == 'not_ready' else 'refused')
        request['revision'] = self.revision
        return True

    def excluded(self, owner, team):
        return sorted(row['zone'] for row in self.claims if row['team'] == team and
                      (row['kind'], row['id']) != tuple(owner))

    def request(self, owner, team, plan, authority_epoch=None):
        owner = tuple(owner)
        zone = plan['zone'] if plan is not None else None
        action = 'claim' if plan is not None else 'release'
        owned = next((row['zone'] for row in self.claims if
                      (row['kind'], row['id']) == owner), None)
        previous = self.requests.get(owner)
        if owned == zone and not (zone is None and previous and previous['zone'] is not None):
            return 'granted'
        now = float(self.clock())
        if previous is not None and previous['zone'] == zone:
            if previous.get('result') == 'refused' and previous['revision'] == self.revision:
                return 'refused'
            if now-previous['at'] < 1.:
                return 'pending'
        self.sequence += 1
        packet = dict(type='spg_parking_request', round_id=self.round_id,
            seq=self.sequence, actor_kind=owner[0], actor_id=owner[1],
            action=action, plan=copy.deepcopy(plan))
        if authority_epoch is not None:
            packet['authority_epoch'] = authority_epoch
        if self.send(packet):
            self.requests[owner] = dict(seq=self.sequence, zone=zone, at=now,
                result='pending', revision=self.revision)
        return 'pending'
