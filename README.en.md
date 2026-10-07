# World Walker

[中文](README.md) | **English**

---

*World Walker* is an AI-driven text interaction game engine. World evolution is driven by 15 academic disciplines and 85+ formulas — every player decision is processed through mathematical models, and the world emerges its own story naturally, without pre-written branches.

Keywords: `AI text adventure` `interactive fiction engine` `emergent narrative` `cognitive architecture` `game AI` `world simulation` `behavioral economics` `evolutionary dynamics` `systems thinking`

---

## Quick Start

```bash
# List commands
PYTHONPATH=. python3 engine.py --help

# 14 commands at a glance
PYTHONPATH=. python3 engine.py combat    --state game.json --attacker player --defender goblin
PYTHONPATH=. python3 engine.py trade     --state game.json --location market --item potion --quantity 3 --direction buy --entity player
PYTHONPATH=. python3 engine.py social    --state game.json --actor player --target npc --event help
PYTHONPATH=. python3 engine.py karma     --state game.json --actor player --karma_type murder_innocent
PYTHONPATH=. python3 engine.py tick      --state game.json
PYTHONPATH=. python3 engine.py flow      --state game.json
PYTHONPATH=. python3 engine.py identity  --state game.json
PYTHONPATH=. python3 engine.py narrative --state game.json
PYTHONPATH=. python3 engine.py world_state  --state game.json
PYTHONPATH=. python3 engine.py panarchy  --state game.json
PYTHONPATH=. python3 engine.py moral_update   --state game.json
PYTHONPATH=. python3 engine.py cognition   --state game.json --entity player
PYTHONPATH=. python3 engine.py merit     --state game.json --aid 0.8 --sincerity 0.9
PYTHONPATH=. python3 engine.py info_weight --state game.json --probability 0.05
```

---

## Project Structure

```
game_engine/
├── engine.py                     # CLI entry (14 commands)
├── state_schema.py               # State schema + helpers
├── demo_state.json               # Demo game state
├── GAME_MASTER_PROTOCOL.md       # AI Agent call protocol
└── rules/                        # 85+ academic formulas as Python
    ├── combat.py                 #    combat / hit / crit
    ├── economy.py                #    economy / supply / demand
    ├── social.py                 #    social 2D relations
    ├── karma.py                  #    causal debt (karma)
    ├── cognition.py              #    cognitive science
    ├── world_dynamics.py         #    world evolution (chaos/Panarchy/PID)
    ├── social_extended.py        #    extended social (Haidt/Milgram/Bandura)
    ├── cultural_evolution.py     #    cultural evolution (DIT/memes/ratchet)
    ├── systems_feedback.py       #    systems feedback (Meadows 12/NAT)
    └── narrative_engine.py       #    emergent narrative (Bartle/events)
```

---

## Academic Coverage

85+ formulas across 15 disciplines:

| Discipline | Core Theories | File | Lines |
|------------|--------------|------|-------|
| Cognitive Science | Kahneman dual-system, Prospect Theory, ACT-R memory, Flow | cognition.py | 235 |
| Chaos / Complex Systems | Lorenz attractor, Lyapunov exponent, Logistic map, Panarchy, PID | world_dynamics.py | 275 |
| Moral Psychology | Haidt 6-dim, Tajfel, Bandura, Milgram, Cialdini | social_extended.py | 202 |
| Evolutionary Dynamics | Price equation, Hamilton, ESS, Red Queen | world_dynamics.py | — |
| Cultural Evolution | DIT, memetics, cultural ratchet, fidelity decay | cultural_evolution.py | 92 |
| Systems Theory | Donella Meadows 12 leverage points, NAT, ANT | systems_feedback.py | 141 |
| Narrative Studies | Emergent narrative, Bartle, narrative transportation | narrative_engine.py | 141 |
| Information Theory | Shannon entropy, KL divergence, event information | world_dynamics.py | — |

---

## Design Principles

1. **Worldview-agnostic** — same math, different narrative vocabulary
2. **Emergence over branching** — the world produces its own story from mechanisms
3. **Agent → Engine → Prose** — engine returns JSON, AI Agent renders it as prose
4. **Fully responsive** — every player action gets a mathematically grounded result

---

## Collaboration

- **For players**: tell the Agent what you want → Agent calls engine → engine returns JSON → Agent narrates what happened
- **For AI Agents**: see [`GAME_MASTER_PROTOCOL.md`](GAME_MASTER_PROTOCOL.md) for the full call protocol, parameters, and response schemas

---

## License

MIT
