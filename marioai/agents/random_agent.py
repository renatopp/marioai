import random
import marioai.core as core

__all__ = ["RandomAgent"]


class RandomAgent(core.Agent):
    def act(self):
        return [0, 1, 0, random.randint(0, 1), random.randint(0, 1)]
