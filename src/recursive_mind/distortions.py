from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Optional

from .mood import Mood
from .state import Thought, ThoughtState


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


@dataclass
class DistortionContext:
    last_thought: Optional[Thought]
    state: ThoughtState
    external: Optional[str] = None


class DistortionEngine:
    """Combines multiple distortion strategies into a single prompt mutation."""

    def __init__(self) -> None:
        self.intrusive_triggers: dict[tuple[str, ...], str] = {
            ("safety", "danger", "risk"): "What if I'm missing the obvious risk?",
            ("loop", "repeat", "stuck"): "I'm spiraling — is this a dead end?",
            ("trust", "lies", "doubt"): "Why do I keep second-guessing everything?",
            ("memory", "remember", "forget"): "Fragments of earlier thoughts keep resurfacing.",
        }
        self.association_map: dict[str, tuple[str, ...]] = {
            "safety": ("alarm bell", "locked door", "red blinking light"),
            "creative": ("unfinished sketch", "midnight brainstorm", "ink-stained hands"),
            "failure": ("cracked mirror", "late apology", "echo of a missed chance"),
            "hope": ("fresh coffee", "morning window", "paper crane"),
            "control": ("tightened grip", "tidy desk", "overwritten diary"),
            "memory": ("dusty attic", "photograph flicker", "taped cassette"),
            "future": ("glowing horizon", "prototype hum", "calculated risk"),
        }
        self.self_doubt_templates = [
            "Am I circling the same conclusion again?",
            "Is this insight meaningful or just noise?",
            "Have I already solved this and forgotten?",
            "Does this contradiction matter right now?",
        ]

    def distort(self, prompt: str, context: DistortionContext) -> str:
        state = context.state
        mood = state.mood_state.mood

        segments: list[str] = []
        segments.append(self._apply_mood(prompt, mood))

        if context.external:
            segments.append(f"Interrupt: {context.external.strip()}")

        memory_fragment = state.memory.recall_fragment()
        if memory_fragment and random.random() < 0.7:
            segments.append(f"Memory echo: {memory_fragment}")

        bias_influence = self._bias_overlay(prompt, state)
        if bias_influence:
            segments.append(bias_influence)

        intrusive = self._intrusive_injection(prompt, state)
        if intrusive:
            segments.append(intrusive)

        if random.random() < 0.4 and context.last_thought:
            associative = self._associative_jump(context.last_thought.text)
            if associative:
                segments.append(f"Tangential drift: {associative}")

        if random.random() < 0.25 and len(state.memory) > 3:
            segments.append(f"Overload: {state.memory.overload()}")

        if random.random() < 0.3:
            segments.append(random.choice(self.self_doubt_templates))

        return "\n".join(segment for segment in segments if segment)

    def _apply_mood(self, prompt: str, mood: Mood) -> str:
        mood_filters = {
            Mood.CALM: lambda text: text,
            Mood.CURIOUS: lambda text: text + " What if there's a hidden angle?",
            Mood.ANXIOUS: lambda text: f"{text} I'm uneasy about where this leads.",
            Mood.MELANCHOLIC: lambda text: f"{text} Everything feels slightly faded.",
            Mood.IRRITATED: lambda text: f"{text} Why am I repeating myself?",
            Mood.INSPIRED: lambda text: f"{text} There's a pulse of possibility here.",
        }
        return mood_filters[mood](prompt.strip())

    def _bias_overlay(self, prompt: str, state: ThoughtState) -> Optional[str]:
        if not state.biases.traits:
            return None
        overlays = []
        for bias, strength in state.biases.traits.items():
            if strength == 0:
                continue
            if bias == "paranoia":
                overlays.append(self._paranoia_overlay(prompt, strength))
            elif bias == "hope":
                overlays.append(self._hope_overlay(prompt, strength))
            elif bias == "self_doubt":
                overlays.append(self._self_doubt_overlay(prompt, strength))
            elif bias == "nostalgia":
                overlays.append(self._nostalgia_overlay(prompt, strength))
        overlays = [item for item in overlays if item]
        if not overlays:
            return None
        return "Bias drift: " + " ".join(overlays)

    def _paranoia_overlay(self, prompt: str, strength: float) -> str:
        return f"Paranoia{x_strength(strength)}: double-checking motives."

    def _hope_overlay(self, prompt: str, strength: float) -> str:
        return f"Hope{x_strength(strength)}: maybe there's a breakthrough close by."

    def _self_doubt_overlay(self, prompt: str, strength: float) -> str:
        return f"Self-doubt{x_strength(strength)}: am I fabricating clarity?"

    def _nostalgia_overlay(self, prompt: str, strength: float) -> str:
        return f"Nostalgia{x_strength(strength)}: echoing something I nearly remembered."

    def _intrusive_injection(self, prompt: str, state: ThoughtState) -> Optional[str]:
        lowered = prompt.lower()
        for keywords, message in self.intrusive_triggers.items():
            if _contains_any(lowered, keywords):
                state.intrusive_budget = max(state.intrusive_budget, 2)
                return f"Intrusive thought: {message}"
        if state.intrusive_budget > 0:
            state.intrusive_budget -= 1
            return f"Intrusive residue: {random.choice(list(self.intrusive_triggers.values()))}"
        return None

    def _associative_jump(self, source_text: str) -> Optional[str]:
        tokens = re.findall(r"[a-zA-Z']{4,}", source_text.lower())
        random.shuffle(tokens)
        for token in tokens:
            if token in self.association_map:
                return random.choice(self.association_map[token])
        if tokens:
            token = random.choice(tokens[:3])
            return f"{token} -> {token[::-1]}"
        return None


def x_strength(value: float) -> str:
    magnitude = abs(value)
    if magnitude < 0.15:
        return ""
    if magnitude < 0.4:
        return " (persistent)"
    if magnitude < 0.7:
        return " (insistent)"
    return " (overpowering)"
