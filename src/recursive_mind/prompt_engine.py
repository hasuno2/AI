from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from .distortions import DistortionContext, DistortionEngine
from .mood import Mood
from .state import ThoughtState


@dataclass
class PromptEngine:
    """
    Transforms the last thought into a new prompt using the distortion engine.
    """

    distortion_engine: DistortionEngine

    def build_prompt(
        self,
        last_output: str,
        state: ThoughtState,
        external: Optional[str] = None,
    ) -> str:
        if not last_output.strip():
            last_output = "..."
        context = DistortionContext(
            last_thought=state.memory.latest(),
            state=state,
            external=external,
        )
        distorted = self.distortion_engine.distort(last_output, context)
        return distorted


class SyntheticThinker:
    """
    A very small thought synthesizer that rewrites prompts into new internal thoughts.
    """

    def respond(self, prompt: str, mood: Mood) -> str:
        lines = [line.strip() for line in prompt.splitlines() if line.strip()]
        if not lines:
            return "Silence feels safer than unfinished reasoning."

        primary = lines[0]
        supporting = " ".join(lines[1:3])

        templates = {
            Mood.CALM: "{primary}. Let me quietly trace that to {direction}.",
            Mood.CURIOUS: "{primary}? Maybe the path forks toward {direction}.",
            Mood.ANXIOUS: "{primary}. I keep scanning for what collapses next near {direction}.",
            Mood.MELANCHOLIC: "{primary}. It tastes like memories of {direction}.",
            Mood.IRRITATED: "{primary}. Why is {direction} still unresolved?",
            Mood.INSPIRED: "{primary}! I can almost sculpt {direction} out of this momentum.",
        }
        direction = self._sample_direction(supporting or primary)
        template = templates[mood]
        return template.format(primary=primary, direction=direction)

    def _sample_direction(self, text: str) -> str:
        tokens = [token.strip(",.?!") for token in text.split() if len(token) > 3]
        if not tokens:
            return "the unspoken edge"
        if len(tokens) == 1:
            return tokens[0]
        return " / ".join(random.sample(tokens, k=min(2, len(tokens))))
