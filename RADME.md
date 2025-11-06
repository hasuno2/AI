# Recursive Mind Games

An experimental playground for modelling an artificial mind that recursively feeds on its own thoughts. Each iteration re-enters the loop with distorted prompts influenced by memory decay, mood drift, persistent biases, intrusive thoughts, and occasional environmental interrupts.

## How It Works
- **Prompt recursion** – The engine rewrites its latest thought into the next prompt instead of relying on fresh user input.
- **Stateful memory** – Recent thoughts stick; old ones decay into hazy fragments that may resurface or overload the current prompt.
- **Mood dynamics** – Mood drifts in response to stimuli, tinting future prompts with calm clarity, anxious worry, irritation, or sudden inspiration.
- **Bias layer** – Persistent leanings (paranoia, hope, self-doubt, nostalgia) skew interpretations and occasionally surface as meta-commentary.
- **Intrusive thoughts** – Keyword-triggered interjections capture spiralling doubt or half-remembered warnings.
- **Environmental noise** – An interrupt handler injects outside events on a cooldown to anchor the loop in a pseudo-world.

## Running the Simulation
```bash
PYTHONPATH=src python -m recursive_mind.main "What is the safest path forward?" --steps 5
```

### Useful Flags
- `--steps N` – Number of recursive passes (default: 8).
- `--no-interrupts` – Disable outside world injections.
- `--seed SEED` – Seed randomness for reproducible runs.
- `--mood MOOD` – Force a starting mood (`calm`, `curious`, `anxious`, `melancholic`, `irritated`, `inspired`).
- `--bias NAME=WEIGHT` – Adjust bias strengths (repeatable).

Each iteration prints the mutated prompt and the synthesised thought, letting you trace how memory fragments, biases, and mood colouring evolve the internal monologue.

## Stretch Ideas
- Swap the `SyntheticThinker` for a real language model.
- Persist and visualise state over multiple runs.
- Replace canned interrupts with live data streams.
- Add a reflective mode where the agent summarises its own wanderings.

This is intentionally a prototype—the fun comes from tweaking the distortion strategies and watching emergent behaviour wobble between insight and existential loop.
