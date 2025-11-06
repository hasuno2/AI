from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class Mood(Enum):
    CALM = "calm"
    CURIOUS = "curious"
    ANXIOUS = "anxious"
    MELANCHOLIC = "melancholic"
    IRRITATED = "irritated"
    INSPIRED = "inspired"

    @property
    def tone_hint(self) -> str:
        hints = {
            Mood.CALM: "softly contemplative",
            Mood.CURIOUS: "questioning",
            Mood.ANXIOUS: "uneasy",
            Mood.MELANCHOLIC: "wistful",
            Mood.IRRITATED: "impatient",
            Mood.INSPIRED: "buoyant",
        }
        return hints[self]


def _weighted_choice(items: Iterable[tuple[Mood, float]]) -> Mood:
    moods, weights = zip(*items)
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0.0
    for mood, weight in zip(moods, weights):
        upto += weight
        if r <= upto:
            return mood
    return moods[-1]


@dataclass
class MoodState:
    """Tracks current mood and allows small random drifts."""

    mood: Mood = Mood.CALM

    def mutate(self, stimulus: str | None = None) -> Mood:
        """
        Drift mood in response to stimulus text. Returns the new mood.
        Mood transitions are biased by keywords and a small random walk.
        """
        drift = {
            Mood.CALM: [(Mood.CALM, 0.4), (Mood.CURIOUS, 0.2), (Mood.MELANCHOLIC, 0.15), (Mood.INSPIRED, 0.25)],
            Mood.CURIOUS: [(Mood.CURIOUS, 0.35), (Mood.INSPIRED, 0.25), (Mood.CALM, 0.2), (Mood.ANXIOUS, 0.2)],
            Mood.ANXIOUS: [(Mood.ANXIOUS, 0.45), (Mood.IRRITATED, 0.2), (Mood.MELANCHOLIC, 0.2), (Mood.CALM, 0.15)],
            Mood.MELANCHOLIC: [(Mood.MELANCHOLIC, 0.4), (Mood.CALM, 0.25), (Mood.ANXIOUS, 0.2), (Mood.CURIOUS, 0.15)],
            Mood.IRRITATED: [(Mood.IRRITATED, 0.4), (Mood.ANXIOUS, 0.2), (Mood.MELANCHOLIC, 0.2), (Mood.CALM, 0.2)],
            Mood.INSPIRED: [(Mood.INSPIRED, 0.45), (Mood.CURIOUS, 0.2), (Mood.CALM, 0.2), (Mood.IRRITATED, 0.15)],
        }

        if stimulus:
            lowered = stimulus.lower()
            if any(token in lowered for token in ("deadline", "danger", "risk", "threat")):
                bias = Mood.ANXIOUS
            elif any(token in lowered for token in ("sunrise", "hope", "success", "dream")):
                bias = Mood.INSPIRED
            elif any(token in lowered for token in ("bored", "stuck", "loop", "repeat")):
                bias = Mood.IRRITATED
            elif any(token in lowered for token in ("loss", "regret", "alone", "memory")):
                bias = Mood.MELANCHOLIC
            else:
                bias = None
            if bias:
                # Increase weight for the biased mood subtly
                weighted = []
                for candidate, weight in drift[self.mood]:
                    if candidate == bias:
                        weighted.append((candidate, weight + 0.25))
                    else:
                        weighted.append((candidate, weight))
                drift[self.mood] = weighted

        self.mood = _weighted_choice(drift[self.mood])
        return self.mood
