import random
from typing import List
import marioai.core as core
import numpy as np
import pandas as pd
__all__ = ['BaseAgent']


class BaseAgent(core.Agent):

    def __init__(
        self,
        window_size: int = 4,
        max_dist: int = 2,
        player_pos: int = 11):
        super().__init__()
        self.frames = 0
        self.window_size = window_size
        self.max_dist = max_dist
        self.player_pos = player_pos
        self.objects = {
            "soft": [-11,],
            "hard": [20, -10],
            "enemy": [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15],
            "brick": [16, 21],
            "projetil": [25],
        }
        self.state = None
        self.frames = 0

    def sense(self, obs: List):
        super().sense(obs)
        self.state = self.build_state()

    def build_state(self):
        """Build state from level scene"""
        ground_pos = self._get_ground()
        state = {
                 "episode_starts": (self.level_scene != 0).any(),
                 "on_ground": self.on_ground,
                 "can_jump": self.can_jump,
                 "episode_over": self.episode_over}

        for o_name, o_values in self.objects.items():
            for dist in range(1, self.max_dist + 1):
                state[f"{o_name}_{dist}"] = self._is_near(o_values, dist)
        for dist in range(1, self.max_dist + 1):
                state[f"has_role_near_{dist}"] = self._has_role(ground_pos, dist)
        return pd.Series(state)

    def _is_near(self, objects, dist):
        for i in range(1, 4):
            x = max(0, self.player_pos - i)
            y = min(self.level_scene.shape[0], self.player_pos + dist)
            if self.level_scene[x, y] in objects:
                return True
        return False

    def _has_role(self, ground_pos, dist):
        y = min(self.level_scene.shape[0], self.player_pos + dist)
        return (self.level_scene[ground_pos:, y] == 0).all()

    def _get_ground(self):
        start, end = 11 - self.window_size, 11 + self.window_size
        if self.on_ground:
            ground_pos = 12
        else:
            is_ground = (self.level_scene[start:, start:end] == -10)*1
            is_ground = np.nonzero(is_ground)
            if is_ground[0].shape[0]:
                ground_pos = is_ground[0][0] + start
            else:
                ground_pos = 10
        return ground_pos

    def act(self):
        # [backward, forward, crouch, jump, speed/bombs]
        return [0, 1, 0, random.randint(0, 1), random.randint(0, 1)]