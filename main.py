# pylint: disable=logging-fstring-interpolation
import logging

from stable_baselines3 import A2C, DQN

import marioai.agents as agents
import marioai.core as core
from marioai.gym import MarioEnv
import click

logger = logging.getLogger(__name__)
environment_options = [
    click.option('--level_difficulty', '-ld','level_difficulty', default=0, type=int),
    click.option('--mario_mode', '-mm', 'mario_mode', default=0, type=int),
    click.option('--time_limit', '-tl', 'time_limit', default=0, type=int),
    click.option('--max_fps', '-fps', 'max_fps', default=720, type=int),
]

def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options

@click.group()
def cli():
  pass

@click.command(name='mc')
@add_options(environment_options)
@click.option('--response_delay', '-rd', 'response_delay', default=0, type=int)
def monte_carlo(
    level_difficulty: int,
    mario_mode: int,
    time_limit: int,
    response_delay: int,
    max_fps: int
):
    task = core.Task(max_dist=4)
    mc_model = agents.MonteCarloAgent(
        2, 0.9, min_epsilon=0.3, reward_threshold=2, reward_increment=0.5
    )
    mc_model = mc_model.fit(
        task=task,
        level_difficulty=level_difficulty,
        mario_mode=mario_mode,
        time_limit=time_limit,
        response_delay=response_delay,
        max_fps=max_fps,
    )


@click.command(name='dqn')
@add_options(environment_options)
@click.option('--total_timesteps', '-tt', 'total_timesteps', default=100000)
@click.option('--log_interval', '-li', 'log_interval', default=4)
def dqn_model(
    level_difficulty: int,
    mario_mode: int,
    time_limit: int,
    max_fps: int,
    total_timesteps: int,
    log_interval: int,
):
    env = MarioEnv(
        level_difficulty=level_difficulty, 
        mario_mode=mario_mode, 
        time_limit=time_limit, 
        max_fps=max_fps
    )
    model = DQN(
        "MlpPolicy", env, verbose=1,
        learning_rate=0.0001, buffer_size=1000000,
        learning_starts=50000, batch_size=32, tau=1.0,
        gamma=0.99, train_freq=4, gradient_steps=1, target_update_interval=10000,
        exploration_fraction=0.1, exploration_initial_eps=1.0,
        exploration_final_eps=0.05, max_grad_norm=10)
    model.learn(total_timesteps=total_timesteps, log_interval=log_interval)
    env.close()


def _run_env():
    env = MarioEnv(level_difficulty=0, mario_mode=0, time_limit=50, max_fps=720)
    observation = env.reset()
    for _ in range(10000):
        action = env.action_space.sample()  # User-defined policy function
        observation, reward, done, info = env.step(action)
        if done:
            observation = env.reset()
    env.close()


cli.add_command(monte_carlo)
cli.add_command(dqn_model)

if __name__ == "__main__":
    cli()
