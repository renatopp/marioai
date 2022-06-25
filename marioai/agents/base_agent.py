import random
from typing import List

import numpy as np

import marioai.core as core

__all__ = ["BaseAgent"]


class BaseAgent(core.Agent):
    def __init__(self):
        super().__init__()
        self.frames = 0

        self.state = None
        self.frames = 0
        self.actions = []
        self.states = []
        self.rewards = []

    def sense(self, state):
        self.state = state
        self.states.append(self.state)

    def act(self):
        # [backward, forward, crouch, jump, speed/bombs]
        action = [0, 1, 0, random.randint(0, 1), random.randint(0, 1)]
        self.actions.append(action)
        return action

    def give_rewards(self, reward, cum_reward):
        self.rewards.append(reward)
        return super().give_rewards(reward, cum_reward)
