# -*- coding: utf-8 -*-
"""Fair engine-owned quotas for optional shared attack-policy work.

Only scheduling state lives here. Candidate rows, native proof, ammunition,
NEXT and search clocks remain private to each control binding. Current-pose
foreground evaluation and actual first-edge admission do not consume these
quotas. Speculative stationary-turn proofs share a separate fair queue.
"""
from collections import deque


BACKGROUND_CANDIDATES_PER_FRAME = 8
BACKGROUND_CANDIDATES_PER_ACTOR = 2
ATOMIC_ACTORS_PER_FRAME = 1
STATIONARY_ACTORS_PER_FRAME = 4


class EvaluationBudget(object):
    def __init__(self):
        self.frame = None
        self.alive = set()
        self._background_waiting = deque()
        self._atomic_waiting = deque()
        self._background_reserved = {}
        self._background_claimed = {}
        self._background_allocated = 0
        self._atomic_reserved = None
        self._atomic_claimed = None
        self._stationary_waiting = deque()
        self._stationary_reserved = set()
        self._stationary_claimed = set()

    @staticmethod
    def _prune(queue, alive):
        return deque(actor for actor in queue if actor in alive)

    def begin(self, frame, actors):
        """Open one control callback; repeated/actor-local begin is a no-op.

        Deferred requesters precede new requests in the following callback.
        A reserved requester which no longer calls the policy loses that
        reservation at the next callback, so inactive work cannot block the
        queue permanently.  Dead identities are removed before reservation.
        """
        if frame == self.frame:
            return False
        self.frame = frame
        self.alive = set(int(actor) for actor in actors)
        self._background_waiting = self._prune(self._background_waiting, self.alive)
        self._atomic_waiting = self._prune(self._atomic_waiting, self.alive)
        self._background_reserved = {}
        self._background_claimed = {}
        self._background_allocated = 0
        while (self._background_waiting and self._background_allocated <
               BACKGROUND_CANDIDATES_PER_FRAME):
            actor = self._background_waiting.popleft()
            self._background_reserved[actor] = BACKGROUND_CANDIDATES_PER_ACTOR
            self._background_allocated += BACKGROUND_CANDIDATES_PER_ACTOR
        self._atomic_reserved = (self._atomic_waiting.popleft()
                                 if self._atomic_waiting else None)
        self._atomic_claimed = None
        self._stationary_waiting = self._prune(self._stationary_waiting, self.alive)
        self._stationary_reserved = set()
        self._stationary_claimed = set()
        while (self._stationary_waiting and len(self._stationary_reserved) <
               STATIONARY_ACTORS_PER_FRAME):
            self._stationary_reserved.add(self._stationary_waiting.popleft())
        return True

    def stationary(self, actor):
        """Admit future-pose work, without refilling its actor-local caps.

        Repeated calls by an admitted actor refer to the same callback grant.
        Its planner keeps one wall/sample budget across those calls and any
        late physics slices. A deferred proof remains unknown, never clear.
        """
        actor = int(actor)
        if actor not in self.alive:
            return False
        if actor in self._stationary_claimed:
            return True
        if actor in self._stationary_reserved:
            self._stationary_reserved.remove(actor)
        elif len(self._stationary_reserved) + len(self._stationary_claimed) < STATIONARY_ACTORS_PER_FRAME:
            if actor in self._stationary_waiting:
                self._stationary_waiting.remove(actor)
        else:
            if actor not in self._stationary_waiting:
                self._stationary_waiting.append(actor)
            return False
        self._stationary_claimed.add(actor)
        return True

    def background(self, actor, maximum):
        actor = int(actor)
        maximum = max(0, min(int(maximum), BACKGROUND_CANDIDATES_PER_ACTOR))
        if actor not in self.alive or not maximum or actor in self._background_claimed:
            return 0
        reserved = self._background_reserved.pop(actor, None)
        if reserved is None:
            if actor not in self._background_waiting:
                self._background_waiting.append(actor)
            if self._background_allocated >= BACKGROUND_CANDIDATES_PER_FRAME:
                return 0
            # Existing reservations already account for earlier waiters.
            # A new request can spend only the unreserved part of this frame.
            self._background_waiting.remove(actor)
            reserved = maximum
            self._background_allocated += reserved
        granted = min(maximum, reserved)
        self._background_claimed[actor] = granted
        return granted

    def atomic(self, actor):
        """Reserve one new atomic slice; never renew its caps in this frame."""
        actor = int(actor)
        if actor not in self.alive or self._atomic_claimed == actor:
            return False
        if self._atomic_reserved is None and self._atomic_claimed is None:
            self._atomic_reserved = actor
        if self._atomic_reserved == actor and self._atomic_claimed is None:
            self._atomic_claimed = actor
            self._atomic_reserved = None
            return True
        if actor not in self._atomic_waiting:
            self._atomic_waiting.append(actor)
        return False

    def receipt(self):
        return dict(frame=self.frame, background_limit=BACKGROUND_CANDIDATES_PER_FRAME,
            background_grants=dict(self._background_claimed),
            background_used=sum(self._background_claimed.values()),
            background_waiting=tuple(self._background_waiting),
            atomic_actor=self._atomic_claimed,
            atomic_waiting=tuple(self._atomic_waiting),
            stationary_limit=STATIONARY_ACTORS_PER_FRAME,
            stationary_actors=tuple(sorted(self._stationary_claimed)),
            stationary_waiting=tuple(self._stationary_waiting))
