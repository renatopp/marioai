import random
from typing import List
import marioai.core as core
import numpy as np

__all__ = ["BaseAgent"]


class BaseAgent(core.Agent):
    def __init__(self, window_size: int = 4, max_dist: int = 2, player_pos: int = 11):
        super().__init__()
        self.frames = 0
        self.window_size = window_size
        self.max_dist = max_dist
        self.player_pos = player_pos
        self._action_pool = np.array([
            # [backward, forward, crouch, jump, speed/bombs]
            [0, 0, 0, 0, 0], # do nothing
            [0, 0, 0, 1, 0], # jump
            [0, 0, 0, 0, 1], # bombs
            [0, 0, 1, 0, 0], # crouch
            [0, 0, 1, 0, 1], # crouch and bombs
            [0, 0, 0, 1, 1], # jump and bombs/speed
            [0, 1, 0, 0, 0], # move forward
            [0, 1, 0, 0, 1], # move forward and bombs/speed
            [0, 1, 0, 1, 0], # jump forward
            [0, 1, 0, 1, 1], # jump forward and bombs/speed
            [1, 0, 0, 0, 0], # move backward
            [1, 0, 0, 0, 1], # move backward and bombs/speed
            [1, 0, 0, 1, 0], # jump backward
            [1, 0, 0, 1, 1], # jump backward and bombs/speed
        ])
        self.objects = {
            "soft": [
                -11,
            ],
            "hard": [20, -10],
            "enemy": [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15],
            "brick": [16, 21],
            "projetil": [25],
        }
        self.state = None
        self.frames = 0
        self.actions = []
        self.states = []
        self.rewards = []

    def filter_actions(self) -> np.array:
        """This function filter the action pool"""
        action_pool = np.copy(self._action_pool)
        if not self.state["can_jump"]:
            action_pool = action_pool[action_pool[:, 3] == 0]
        return action_pool

    def sense(self, obs: List):
        super().sense(obs)
        self.state = self.build_state()
        self.states.append(self.state)

    def build_state(self):
        """Build state from level scene"""
        ground_pos = self._get_ground()
        state = {
            "region_x": int(self.mario_floats[0]//250),
            #"y": int(self.mario_floats[1]),
            "episode_starts": (self.level_scene != 0).any(),
            "on_ground": self.on_ground,
            "can_jump": self.can_jump,
            "episode_over": self.episode_over,
        }

        for o_name, o_values in self.objects.items():
            for dist in range(1, self.max_dist + 1):
                state[f"{o_name}_{dist}"] = self._is_near(o_values, dist)
        for dist in range(1, self.max_dist + 1):
            state[f"has_role_near_{dist}"] = self._has_role(ground_pos, dist)
        return state

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
            is_ground = (self.level_scene[start:, start:end] == -10) * 1
            is_ground = np.nonzero(is_ground)
            if is_ground[0].shape[0]:
                ground_pos = is_ground[0][0] + start
            else:
                ground_pos = 10
        return ground_pos

    def act(self):
        # [backward, forward, crouch, jump, speed/bombs]
        action = [0, 1, 0, random.randint(0, 1), random.randint(0, 1)]
        self.actions.append(action)
        return action

    def give_rewards(self, reward, cum_reward):
        self.rewards.append(reward)
        return super().give_rewards(reward, cum_reward)