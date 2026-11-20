"""Player planning roles for the exact #1513 gun/shell combinations.

These roles do not alter a shell's physical kind, damage or magazine rules.
The five HE exceptions were selected from the pinned client's mounted shots;
shell names alone cannot identify penetration because guns can share a shell.
"""
from __future__ import division

from .. import combat_rules


FULL = 'full'
SINGLE_POINT = 'single_point'
HE = 'HIGH_EXPLOSIVE'
FULL_VALIDATION_HE = frozenset((
    ('uk:_183mm_L4', 'uk:_183mm_HESH'),
    ('uk:_183mm_AT_Gun', 'uk:_183mm_HESH'),
    ('uk:_105mm_Gun_L7', 'uk:_105mm_HESH_L7'),
    ('uk:_105mm_AT_Gun_L7', 'uk:_105mm_HESH_L7'),
    ('uk:_5_5inch_AT_Gun', 'uk:_5_5inch_HESH_Mk_1'),
))


def validation_mode(gun_identity, shell_identity, kind):
    """Classify the mounted shot without inferring identity from slot/price."""
    if kind != HE:
        return FULL
    return FULL if (gun_identity, shell_identity) in FULL_VALIDATION_HE else SINGLE_POINT


def mounted_identity(nation, name):
    if not nation or not name:
        return None
    name = str(name)
    if ':' in name:
        return name if name.split(':', 1)[0] == nation else None
    return nation + ':' + name


def mounted_round(index, shot, nation, gun_identity):
    shell = combat_rules.legacy_shot(shot).get('shell') or {}
    identity = mounted_identity(nation, shell.get('name'))
    return dict(index=index, shot=shot, gun_identity=gun_identity, shell_identity=identity,
                is_he=combat_rules.is_he(shot), piercing=combat_rules.range_piercing(shot, 0.),
                nominal_damage=combat_rules.shell_nominal_damage(shot),
                validation_mode=validation_mode(gun_identity, identity, shell.get('kind')))


def shell_mode(shell):
    """Read the observation's role; unlabelled physical HE uses the default."""
    mode = shell.get('validation_mode')
    if mode in (FULL, SINGLE_POINT):
        return mode
    return SINGLE_POINT if shell.get('is_he') else FULL


def penetration_round(shell):
    """Include reviewed premium HE in the primary penetration sequence."""
    return not shell.get('is_he') or shell_mode(shell) == FULL
