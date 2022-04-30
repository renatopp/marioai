import marioai.core as core

__all__ = ["Runner"]


class Runner:
    """This class runs a experiment."""

    def __init__(self, agent):
        self.task = core.Task()
        self.exp = core.Experiment(self.task, agent)

    def run(self, max_fps=24, level_type=0):
        self.exp.max_fps = max_fps
        self.task.env.level_type = level_type
        rewards = self.exp.do_episodes()
        return rewards

    def close(self):
        self.task.disconnect()
