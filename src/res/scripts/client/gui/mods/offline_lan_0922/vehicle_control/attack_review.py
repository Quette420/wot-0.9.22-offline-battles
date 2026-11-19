"""Vehicle-level armour review; aim points never define the angle anchor."""
from __future__ import division

import math


REVIEW_ANGLE = math.radians(30.)


def angle_difference(first, second):
    if isinstance(first, (tuple, list)):
        dot = sum(a * b for a, b in zip(first, second))
        cross = (first[1] * second[2] - first[2] * second[1],
                 first[2] * second[0] - first[0] * second[2],
                 first[0] * second[1] - first[1] * second[0])
        return math.atan2(math.sqrt(sum(value * value for value in cross)), dot)
    return abs((float(first) - float(second) + math.pi) % (2. * math.pi) - math.pi)


def geometry(source, centre, heading):
    """World centre-line direction and enemy chassis heading, never aim points."""
    delta = tuple(float(centre[index]) - float(source[index]) for index in range(3))
    length = math.sqrt(sum(value * value for value in delta))
    if length <= 1.e-6 or math.isnan(length) or math.isinf(length):
        return None
    heading = float(heading)
    return None if math.isnan(heading) or math.isinf(heading) else (
        tuple(value / length for value in delta), heading)


class AttackReview(object):
    """Keep one completed angle snapshot per enemy and physical weapon owner.

    A shell promotion invalidates that newly mounted shell's old point rows;
    it does not erase valid lower-shell failures used by the return rule.
    Only a completed plate/contact observation establishes an angle anchor.
    """
    def __init__(self):
        self.owner = None
        self.targets = {}
        self.loaded = None
        self.loads = {}
        self.epochs = {}

    def observe(self, frame):
        owner = frame.get('weapon_identity')
        observations = frame.get('review_geometry')
        if owner is None or observations is None:
            return
        if owner != self.owner:
            self.owner, self.targets, self.loads, self.loaded = owner, {}, {}, None
            self.epochs = {}
        loaded = int(frame['loaded'])
        if self.loaded is not None and loaded != self.loaded:
            self.loads[loaded] = self.loads.get(loaded, 0) + 1
        self.loaded = loaded
        identities = frame['review_identities']
        for key in list(self.targets):
            if key not in observations:
                self.epochs[key] = self.targets.pop(key)['epoch'] + 1
        stamps, reasons = {}, {}
        for key, value in observations.items():
            if value is None:
                continue
            identity = identities[key]
            row = self.targets.get(key)
            if row is None or row['identity'] != identity:
                row = self.targets[key] = dict(identity=identity,
                    epoch=self.epochs.get(key, 0), anchor=None)
            anchor = row['anchor']
            if anchor is not None:
                changed = tuple(name for name, before, after in
                    zip(('centre_line', 'enemy_heading'), anchor, value)
                    if angle_difference(before, after) + 1.e-10 >= REVIEW_ANGLE)
                if changed:
                    row.update(epoch=row['epoch'] + 1, anchor=None)
                    reasons[key] = dict(changed=changed, previous=anchor, current=value,
                                        epoch=row['epoch'])
            stamps[key] = (identity, row['epoch'])
        frame['review_stamps'] = stamps
        frame['review_loads'] = dict(self.loads)
        frame['review_reasons'] = reasons

    def commit(self, frame, key):
        row = self.targets.get(key)
        stamp = (frame.get('review_stamps') or {}).get(key)
        value = (frame.get('review_geometry') or {}).get(key)
        if row is None or value is None or stamp != (row['identity'], row['epoch']):
            return False
        if row['anchor'] is None:
            # Use the snapshot actually checked, never a newer pose read at
            # completion. Later changes remain visible to the next observe.
            row['anchor'] = value
        return True


def stamp(frame, shell, target):
    reviewed = (frame.get('review_stamps') or {}).get(target['key'])
    if reviewed is None:
        return None
    signature = shell['signature']
    # The native mode pair may expose another shot object for the same
    # mounted round. Its ballistic/material values, not its address, matter.
    signature = (signature[0], signature[2:])
    return (frame['weapon_identity'], ('review', reviewed[1]), reviewed[0],
            reviewed[1], (signature, frame['review_loads'].get(shell['index'], 0)), None)
