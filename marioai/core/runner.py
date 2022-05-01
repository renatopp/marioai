from typing import List
import marioai.core as core
__all__ = ["Runner"]


class Runner:
    """This class runs a experiment."""

    def __init__(
        self,
        agent: core.Agent,
        max_fps: int =24,
        level_difficult: int = 0,
        level_type: int = 0,
        creatures_enabled: bool = True,
        mario_mode: int = 2,
        level_seed: int = 1,
        time_limit: int = 100,
        visualization: bool = True,
        fitness_values: int = 5,
        response_delay: int = 2):
        """ This class running a mario game

        Args:
            agent (core.Agent): Agent used in game.
            max_fps (int, optional): Game FPS. Defaults to 24.
            level_difficult (int, optional): Level difficult. Defaults to 0.
            level_type (int, optional): Level type. Defaults to 0.
            creatures_enabled (bool, optional): If creatures is enabled. Defaults to True.
            mario_mode (int, optional): Mario mode. Defaults to 2.
            level_seed (int, optional): Random seed to generate levels scenes. Defaults to 1.
            time_limit (int, optional): Time limit. Defaults to 100.
            visualization (bool, optional): If the game will be streamed. Defaults to True.
            fitness_values (int, optional): Fitness value. Defaults to 5.
            response_delay (int, optional): Response delay. Defaults to 2.
        """
        self.task = core.Task()
        self.exp = core.Experiment(self.task, agent)
        # Set experiment values
        self.exp.max_fps = max_fps
        self.exp.response_delay = response_delay
        # Set environments values
        self.task.env.level_difficulty = level_difficult
        self.task.env.level_type = level_type
        self.task.env.creatures_enabled = creatures_enabled
        self.task.env.init_mario_mode = mario_mode
        self.task.env.level_seed = level_seed
        self.task.env.time_limit = time_limit
        self.task.env.visualization = visualization
        self.task.env.fitness_values = fitness_values

    def run(self) -> List:
        """This function execute a game
        Returns:
            List: Rewards
        """
        rewards = self.exp.do_episodes()
        return rewards

    def close(self):
        """This functions close the game
        """
        self.task.disconnect()

    def __del__(self):
        self.close()
