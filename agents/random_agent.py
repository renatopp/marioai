import random
import marioai

__all__ = ['RandomAgent']

class RandomAgent(marioai.Agent):
    def act(self):
        return [0, 1, 0, random.randint(0, 1), random.randint(0, 1)]