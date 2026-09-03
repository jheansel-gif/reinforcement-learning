"""Reference implementations of the building blocks introduced in RL00.

Students implement these themselves as exercises in
``RL00_Problem_Formulation``. Later notebooks import them from here so that
each notebook runs standalone from a fresh kernel.
"""

from abc import ABC, abstractmethod

import gymnasium as gym
import numpy as np
from tqdm import tqdm

from rl_basics.rl_envs.taxi_utils import close_taxi_render, render_taxi
from rl_basics.utils import DOWN, RIGHT, UP

# --------------------------------------------------------------------------
# Policies
# --------------------------------------------------------------------------


class Policy(ABC):
    @abstractmethod
    def get_action(self, state):
        pass


class RandomPolicy(Policy):
    def __init__(self, actions_cardinality):
        self.actions_cardinality = actions_cardinality

    def get_action(self, state):
        return np.random.randint(0, self.actions_cardinality)


class CliffWalkingHeuristicPolicy(Policy):
    def get_action(self, state):
        if state[0] < 3 and state[1] < 11:
            return RIGHT
        elif state[0] == 3 and state[1] == 0:
            return UP
        else:
            return DOWN


# --------------------------------------------------------------------------
# Interaction
# --------------------------------------------------------------------------


def rollout(env: gym.Env, policy: Policy, render=True):
    """Run one episode. Returns (frames,) states, actions, rewards."""
    frames = []

    initial_state, _ = env.reset()

    states = [initial_state]
    actions = []
    rewards = []

    done = False
    while not done:
        if render:
            frames.append(env.render())

        action = policy.get_action(states[-1])
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

        actions.append(action)
        rewards.append(reward)
        states.append(next_state)

    if render:
        return frames, states, actions, rewards
    else:
        return states, actions, rewards


def evaluate_policy(env: gym.Env, policy: Policy, n_runs: int = 100,
                    discount_factor: float = 1.0, display_result: bool = True):
    """Estimate the discounted return of a policy with a 95% confidence interval."""
    mean_discounted_return = 0.0
    sum_squared_diffs = 0.0

    for i in tqdm(range(n_runs), desc="Evaluating Policy"):
        _, _, rewards = rollout(env, policy, render=False)

        discounted_return = 0.0
        for h in range(len(rewards)):
            discounted_return += discount_factor ** h * rewards[h]

        # Welford's algorithm to compute running variance
        diff_from_old_mean = discounted_return - mean_discounted_return
        mean_discounted_return += diff_from_old_mean / (i + 1)

        diff_from_new_mean = discounted_return - mean_discounted_return
        sum_squared_diffs += diff_from_old_mean * diff_from_new_mean

    # Sample standard deviation (Bessel's correction)
    if n_runs > 1:
        std_dev = (sum_squared_diffs / (n_runs - 1)) ** 0.5
    else:
        std_dev = 0.0

    # Margin of error (95% confidence level, z = 1.96)
    margin_of_error = 1.96 * (std_dev / np.sqrt(n_runs)) if n_runs > 0 else 0.0

    if display_result:
        from IPython.display import Markdown, display

        lower_bound = mean_discounted_return - margin_of_error
        upper_bound = mean_discounted_return + margin_of_error
        display(Markdown(
            rf"$J^\pi_\gamma \in [{lower_bound:.2f}, {upper_bound:.2f}]$ w.p. $0.95$"
        ))

    return mean_discounted_return, margin_of_error


# --------------------------------------------------------------------------
# The Milan taxi environment
# --------------------------------------------------------------------------

NUM_ROWS, NUM_COLS = 5, 5
HORIZON = 100

SOUTH, NORTH, EAST, WEST, PICKUP, DROPOFF = 0, 1, 2, 3, 4, 5

INTERNAL_WALLS = [
    ((0, 1), (0, 2)), ((1, 1), (1, 2)),
    ((3, 0), (3, 1)), ((4, 0), (4, 1)),
    ((3, 2), (3, 3)), ((4, 2), (4, 3)),
]

LOCS = [(0, 0), (0, 4), (4, 0), (4, 3)]

PASS_IN_TAXI = 4


def check_wall(row, col, new_row, new_col):
    return ((row, col), (new_row, new_col)) in INTERNAL_WALLS or \
        ((new_row, new_col), (row, col)) in INTERNAL_WALLS


class MilanTaxiEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.state = None
        self.time_step = 0
        self.lastaction = None
        self._delivered_passengers = 0

    def reset(self):
        self._delivered_passengers = 0
        self.time_step = 0
        self.lastaction = None

        taxi_row = np.random.randint(0, NUM_ROWS)
        taxi_col = np.random.randint(0, NUM_COLS)
        pass_idx, dest_idx = self._spawn_new_passenger()

        self.state = (taxi_row, taxi_col, pass_idx, dest_idx)

        return self.state, {}

    def step(self, action):
        row, col, pass_idx, dest_idx = self.state

        new_row, new_col, new_pass_idx, new_dest_idx, reward, dest_reached = \
            self._transitions(row, col, pass_idx, dest_idx, action)

        self.lastaction = action

        self.time_step += 1
        truncated = self.time_step >= HORIZON

        if dest_reached:
            self._delivered_passengers += 1
            if not truncated:
                new_pass_idx, new_dest_idx = self._spawn_new_passenger()

        self.state = (new_row, new_col, new_pass_idx, new_dest_idx)

        return self.state, reward, False, truncated, {
            "delivered_passengers": self._delivered_passengers
        }

    def _spawn_new_passenger(self):
        pickup, dropoff = np.random.choice(4, size=2, replace=False)
        return int(pickup), int(dropoff)

    def _transitions(self, row, col, pass_idx, dest_idx, action):
        new_row, new_col = row, col
        new_pass_idx = pass_idx
        dest_reached = False
        reward = -1

        if action == NORTH:
            new_row = max(row - 1, 0)
        elif action == SOUTH:
            new_row = min(row + 1, NUM_ROWS - 1)
        elif action == EAST:
            new_col = min(col + 1, NUM_COLS - 1)
        elif action == WEST:
            new_col = max(col - 1, 0)
        elif action == PICKUP:
            if pass_idx != PASS_IN_TAXI and (new_row, new_col) == LOCS[pass_idx]:
                new_pass_idx = PASS_IN_TAXI
            else:
                reward = -10
        elif action == DROPOFF:
            if pass_idx == PASS_IN_TAXI and (new_row, new_col) == LOCS[dest_idx]:
                reward = 20
                dest_reached = True
            else:
                reward = -10

        if check_wall(row, col, new_row, new_col):
            new_row, new_col = row, col

        return new_row, new_col, new_pass_idx, dest_idx, reward, dest_reached

    def render(self):
        return render_taxi(self.state, self.lastaction)

    def close(self):
        close_taxi_render()
