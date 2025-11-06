from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

from .distortions import DistortionEngine
from .interrupts import InterruptHandler
from .mood import Mood
from .prompt_engine import PromptEngine, SyntheticThinker
from .state import ThoughtState


@dataclass
class StepResult:
    iteration: int
    mood: Mood
    prompt: str
    thought: str
    external: Optional[str] = None


@dataclass
class RecursiveMindEngine:
    """
    Coordinates state, distortions, and synthesis to simulate recursive thinking.
    """

    state: ThoughtState = field(default_factory=ThoughtState)
    distortions: DistortionEngine = field(default_factory=DistortionEngine)
    interrupts: InterruptHandler = field(default_factory=InterruptHandler)
    synthesizer: SyntheticThinker = field(default_factory=SyntheticThinker)
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        if self.seed is not None:
            random.seed(self.seed)
        self.prompt_engine = PromptEngine(self.distortions)

    def reset(self) -> None:
        self.state = ThoughtState()

    def run(
        self,
        initial_thought: str,
        steps: int = 8,
        allow_interrupts: bool = True,
        starting_mood: Optional[Mood] = None,
        bias_overrides: Optional[dict[str, float]] = None,
    ) -> List[StepResult]:
        """
        Execute the recursive loop for a fixed number of iterations.
        """
        self.state = ThoughtState()  # fresh state per run
        if starting_mood:
            self.state.mood_state.mood = starting_mood
        if bias_overrides:
            self.state.biases.adjust(bias_overrides)
        self.state.register(initial_thought)
        current = initial_thought
        results: list[StepResult] = []

        for step_index in range(1, steps + 1):
            self.state.drift_mood(current)
            external = self.interrupts.maybe_interrupt(self.state.iteration) if allow_interrupts else None
            prompt = self.prompt_engine.build_prompt(current, self.state, external=external)
            mood = self.state.mood_state.mood
            response = self.synthesizer.respond(prompt, mood)
            self.state.register(response)
            results.append(
                StepResult(
                    iteration=step_index,
                    mood=mood,
                    prompt=prompt,
                    thought=response,
                    external=external,
                )
            )
            current = response

        return results

    def iterate_until(self, initial_thought: str, predicate, max_steps: int = 20) -> List[StepResult]:
        """
        Run until predicate(state) returns True or max_steps reached.
        """
        all_steps: list[StepResult] = []
        for result in self.run(initial_thought, steps=max_steps):
            all_steps.append(result)
            if predicate(self.state):
                break
        return all_steps
