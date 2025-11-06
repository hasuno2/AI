from __future__ import annotations

import argparse
from typing import Dict

from .engine import RecursiveMindEngine
from .mood import Mood


def parse_bias_overrides(bias_args: list[str]) -> Dict[str, float]:
    overrides: dict[str, float] = {}
    for item in bias_args:
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"Bias override '{item}' must look like name=value")
        name, value = item.split("=", 1)
        try:
            overrides[name.strip()] = float(value)
        except ValueError as exc:  # pragma: no cover - defensive
            raise argparse.ArgumentTypeError(f"Could not parse bias value '{value}'") from exc
    return overrides


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulate a recursive AI mind that mutates its own prompts."
    )
    parser.add_argument("prompt", help="Initial thought to seed the recursive loop.")
    parser.add_argument("--steps", type=int, default=8, help="Number of recursive iterations to run.")
    parser.add_argument(
        "--no-interrupts",
        action="store_true",
        help="Disable environmental interrupts for a cleaner loop.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed the random generator for repeatable runs.",
    )
    parser.add_argument(
        "--mood",
        choices=[mood.value for mood in Mood],
        help="Force the starting mood instead of letting it drift organically.",
    )
    parser.add_argument(
        "--bias",
        action="append",
        default=[],
        metavar="NAME=WEIGHT",
        help="Override a bias weight, e.g. --bias paranoia=0.4 (can repeat).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    starting_mood = Mood(args.mood) if args.mood else None
    bias_overrides = parse_bias_overrides(args.bias) if args.bias else {}

    engine = RecursiveMindEngine(seed=args.seed)
    results = engine.run(
        initial_thought=args.prompt,
        steps=args.steps,
        allow_interrupts=not args.no_interrupts,
        starting_mood=starting_mood,
        bias_overrides=bias_overrides or None,
    )

    print("=" * 72)
    print(f"Initial prompt: {args.prompt}")
    print(f"Starting mood: {(starting_mood.value if starting_mood else 'auto')}")
    print(f"Bias overrides: {bias_overrides or 'default profile'}")
    print("=" * 72)

    for step in results:
        print(f"[{step.iteration:02d}] mood={step.mood.value}")
        if step.external:
            print(f"  external -> {step.external}")
        print("  prompt  -> " + step.prompt.replace("\n", "\n              "))
        print("  thought -> " + step.thought)
        print("-" * 72)


if __name__ == "__main__":
    main()

