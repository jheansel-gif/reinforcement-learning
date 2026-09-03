# RL Basics

A three-part, hands-on introduction to **tabular reinforcement learning**, built around a
*cliff walking* gridworld and a *Milan taxi* environment.

The notebooks are exercise-driven: each one has `⭐ Exercise` cells with the implementation
left blank for you to fill in.

## The notebooks

Work through them in order — each depends on the vocabulary of the one before it.

| # | Notebook | What it covers |
|---|---|---|
| 0 | [`RL00_Problem_Formulation`](notebooks/RL00_Problem_Formulation.ipynb) | MDPs, environments, policies, trajectories, the objective $J_\gamma^\pi$, and the value functions $V_\gamma^\pi$ / $Q_\gamma^\pi$ |
| 1 | [`RL01_Dynamic_Programming`](notebooks/RL01_Dynamic_Programming.ipynb) | Planning with a **known** model: exact policy evaluation, iterative policy evaluation, policy iteration, value iteration |
| 2 | [`RL02_Prediction_and_Control`](notebooks/RL02_Prediction_and_Control.ipynb) | Learning from **samples**: Every-Visit Monte Carlo, TD(0), SARSA, $Q$-learning |

The ordering is deliberate. RL01 computes value functions *exactly*, by solving the linear
system

$$(I - \gamma P^\pi)\, V^\pi = R^\pi,$$

which is possible only because the transition probabilities are known. RL02 then removes that
assumption, and every method in it is the sampled counterpart of something RL01 computed
exactly:

| Dynamic programming (RL01) | Reinforcement learning (RL02) |
| --- | --- |
| Exact solve $(I - \gamma P^\pi)^{-1} R^\pi$ | Every-Visit Monte Carlo |
| Iterative policy evaluation | TD(0) |
| Policy iteration | SARSA |
| Value iteration | $Q$-learning |

Having the exact answer from RL01 means you can *measure* how wrong a sampled estimate is,
rather than eyeballing whether it looks reasonable.

## Setup

The project uses [uv](https://docs.astral.sh/uv/). You do **not** need to install Python
separately — uv reads `requires-python` from `pyproject.toml` and fetches a matching
interpreter automatically.

```powershell
uv sync
.venv\Scripts\Activate.ps1
```

Then launch Jupyter and select the `.venv` kernel:

```powershell
uv run jupyter lab
```

See [`uv_guide.md`](uv_guide.md) for the full workflow — adding dependencies, rebuilding the
environment, and why the notebooks need `%autoreload`.

## Project structure

```
notebooks/
├── RL00_Problem_Formulation.ipynb
├── RL01_Dynamic_Programming.ipynb
└── RL02_Prediction_and_Control.ipynb

src/rl_basics/
├── core.py                     # Policy, rollout, evaluate_policy, MilanTaxiEnv
├── utils.py                    # plotting, animation, env registration
├── imgs/                       # figures and sprites
└── rl_envs/
    ├── custom_cliff.py         # CliffWalking-RLSS-v0
    └── taxi_utils.py           # taxi rendering
```

`rl_basics` is installed in editable mode by `uv sync`, so the notebooks import it directly
and pick up source edits without a reinstall.

> **Note.** `core.py` holds reference implementations of the RL00 exercises. RL02 imports them
> so it runs standalone from a fresh kernel — which does mean the answers to RL00 are readable
> there if you go looking.

## Environments

**Cliff walking** (`CliffWalking-RLSS-v0`) — a $4 \times 12$ grid. The bottom-right cell is the
goal; the rest of the bottom row is a cliff. Every step costs $-1$, falling costs $-100$ and
ends the episode. `reset` places the agent uniformly at random on any non-cliff cell.

**Milan taxi** (`MilanTaxiEnv`) — a $5 \times 5$ gridworld with internal walls where a taxi picks
up and drops off passengers at four landmarks. Each step costs $-1$, an illegal pickup or
dropoff costs $-10$, and a successful delivery earns $+20$. You implement its transition
function in RL00.

## Source

Adapted from the **Reinforcement Learning Summer School 2026 (RLSS26)**, Milan, Italy —
*RL Basics I: Introduction to Reinforcement Learning*.

Original authors (Politecnico di Milano): Enea Gusmeroli, Cristiano Migali, Davide Salaorni,
Gianmarco Tedeschi.

Original materials: [github.com/gianmtedeschi/tutorial-rlss26](https://github.com/gianmtedeschi/tutorial-rlss26)
