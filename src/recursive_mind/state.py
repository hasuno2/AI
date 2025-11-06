from __future__ import annotations

import math
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Iterable, List, Optional

from .mood import Mood, MoodState


@dataclass
class Thought:
    text: str
    iteration: int
    mood: Mood
    weight: float = 1.0
    tags: tuple[str, ...] = ()

    def decayed_copy(self, decay: float) -> "Thought":
        return Thought(
            text=self.text,
            iteration=self.iteration,
            mood=self.mood,
            weight=max(0.01, self.weight * decay),
            tags=self.tags,
        )


@dataclass
class BiasProfile:
    """Persistent leanings that gently skew interpretation."""

    traits: dict[str, float] = field(default_factory=lambda: {
        "paranoia": 0.1,
        "hope": 0.2,
        "self_doubt": 0.15,
        "nostalgia": 0.1,
    })

    def strongest_bias(self) -> Optional[str]:
        if not self.traits:
            return None
        return max(self.traits.items(), key=lambda item: abs(item[1]))[0]

    def adjust(self, deltas: dict[str, float]) -> None:
        for key, delta in deltas.items():
            self.traits[key] = max(-1.0, min(1.0, self.traits.get(key, 0.0) + delta))


class ThoughtMemory:
    """Stores recent thoughts with exponential decay."""

    def __init__(self, maxlen: int = 12, decay: float = 0.82) -> None:
        self._buffer: Deque[Thought] = deque(maxlen=maxlen)
        self.decay = decay

    def __iter__(self) -> Iterable[Thought]:
        return iter(self._buffer)

    def __len__(self) -> int:
        return len(self._buffer)

    def add(self, thought: Thought) -> None:
        decayed: List[Thought] = []
        for t in self._buffer:
            decayed.append(t.decayed_copy(self.decay))
        self._buffer.clear()
        self._buffer.extend(decayed)
        self._buffer.append(thought)

    def latest(self) -> Optional[Thought]:
        if not self._buffer:
            return None
        return self._buffer[-1]

    def recall_fragment(self) -> Optional[str]:
        if not self._buffer:
            return None
        weights = [max(thought.weight, 0.01) for thought in self._buffer]
        total = sum(weights)
        pick = random.uniform(0, total)
        upto = 0.0
        for thought, weight in zip(self._buffer, weights):
            upto += weight
            if upto >= pick:
                return self._mutate_fragment(thought)
        return self._mutate_fragment(self._buffer[-1])

    def _mutate_fragment(self, thought: Thought) -> str:
        tokens = thought.text.split()
        if len(tokens) <= 5:
            fragment = thought.text
        else:
            start = random.randint(0, max(0, len(tokens) - 5))
            end = min(len(tokens), start + random.randint(3, 7))
            fragment = " ".join(tokens[start:end])

        if random.random() < 0.4:
            fragment = fragment.capitalize()
        if random.random() < 0.15:
            fragment = fragment[::-1]
        return fragment

    def overload(self) -> str:
        snippets = []
        for thought in random.sample(list(self._buffer), k=min(3, len(self._buffer))):
            snippets.append(self._mutate_fragment(thought))
        return " / ".join(snippets)


@dataclass
class ThoughtState:
    memory: ThoughtMemory = field(default_factory=ThoughtMemory)
    mood_state: MoodState = field(default_factory=MoodState)
    biases: BiasProfile = field(default_factory=BiasProfile)
    iteration: int = 0
    intrusive_budget: int = 0

    def register(self, text: str) -> Thought:
        mood = self.mood_state.mood
        self.iteration += 1
        weight = math.exp(-self.iteration / 20)
        thought = Thought(text=text, iteration=self.iteration, mood=mood, weight=weight)
        self.memory.add(thought)
        return thought

    def drift_mood(self, stimulus: str | None = None) -> Mood:
        return self.mood_state.mutate(stimulus)
