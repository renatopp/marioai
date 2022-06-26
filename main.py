# pylint: disable=logging-fstring-interpolation
import logging

from stable_baselines3 import A2C, DQN

import marioai
import marioai.agents as agents
import marioai.core as core
from marioai.gym import MarioEnv

logger = logging.getLogger(__name__)


def _monte_carlo():
    task = core.Task(max_dist=4)
    mc_model = agents.MonteCarloAgent(
        2, 0.9, min_epsilon=0.3, reward_threshold=2, reward_increment=0.5
    )
    mc_model = mc_model.fit(
        task=task,
        level_difficult=0,
        mario_mode=0,
        time_limit=10,
        response_delay=0,
        max_fps=720,
    )


def _gym_model():
    env = MarioEnv(level_difficult=0, mario_mode=1, time_limit=150, max_fps=720)
    model = DQN(
        "MlpPolicy", env, verbose=1,
        learning_rate=0.0001, buffer_size=1000000,
        learning_starts=50000, batch_size=32, tau=1.0,
        gamma=0.99, train_freq=4, gradient_steps=1, target_update_interval=10000,
        exploration_fraction=0.1, exploration_initial_eps=1.0,
        exploration_final_eps=0.05, max_grad_norm=10)
    model.learn(total_timesteps=1000000, log_interval=4)
    env.close()


def _run_env():
    env = MarioEnv(level_difficult=0, mario_mode=0, time_limit=50, max_fps=720)
    observation = env.reset()
    for _ in range(10000):
        action = env.action_space.sample()  # User-defined policy function
        observation, reward, done, info = env.step(action)
        if done:
            observation = env.reset()
    env.close()


if __name__ == "__main__":
    # run_env()
    # monte_carlo()
    _gym_model()
