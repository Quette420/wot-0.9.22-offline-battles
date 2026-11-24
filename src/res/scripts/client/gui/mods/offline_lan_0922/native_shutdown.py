"""Retire offline owners before #1513 tears down Messenger and model managers.

guiModsFini runs after resetEntityManager/clearAllSpaces in the pinned client.
Waiting for that callback leaves custom model cycles to the engine's late GC,
after native model managers have already retired. This hook changes only the
offline owner's shutdown boundary; the stock fini still executes once.
"""
from __future__ import print_function
import gc
import sys

_HOOK = None


def install(game, cleanup):
    global _HOOK
    if _HOOK is not None:
        return False
    original = game.fini
    entered = [False]

    def retire_first(*args, **kwargs):
        if entered[0]:
            return None
        entered[0] = True
        try:
            error = cleanup()
            if error is not None:
                raise error
        except Exception as error:
            # Continue stock shutdown, reporting the failure rather than
            # leaving the native process half finalized.
            sys.stdout.write('[Offline LAN 0.9.22] early shutdown failed: %s\n' % error)
        try:
            # Offline callback owners are cancelled and detached above. The
            # native model manager is still live at this collection boundary.
            gc.collect()
        except Exception as error:
            sys.stdout.write('[Offline LAN 0.9.22] early shutdown collection failed: %s\n' % error)
        return original(*args, **kwargs)

    _HOOK = game, original, retire_first
    game.fini = retire_first
    return True
