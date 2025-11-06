from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Iterable, Optional


DEFAULT_EVENTS = (
    "Background notification: rain taps against the window.",
    "News flash: a distant satellite sends garbled telemetry.",
    "Ambient memory: a lullaby hum lingers with no clear origin.",
    "External ping: roommate asks if you're still awake.",
    "Sensor blip: heart rate spikes without explanation.",
    "Static: a half-heard podcast quote loops unexpectedly.",
)


@dataclass
class InterruptHandler:
    """
    Injects occasional external stimuli to simulate environmental noise.
    """

    events: Iterable[str] = field(default_factory=lambda: DEFAULT_EVENTS)
    probability: float = 0.25
    cooldown: int = 2
    _cooldown_counter: int = field(default=0, init=False)

    def maybe_interrupt(self, iteration: int) -> Optional[str]:
        if self._cooldown_counter > 0:
            self._cooldown_counter -= 1
            return None
        if random.random() < self.probability:
            self._cooldown_counter = self.cooldown
            return random.choice(tuple(self.events))
        return None

