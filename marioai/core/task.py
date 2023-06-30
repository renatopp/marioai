import numpy as np

import marioai.core as core

__all__ = ["Task"]


class Task(object):
    """A task handles communication with the environment.

    It decides how to evaluate the observations, potentially returning
    reinforcement rewards or fitness values. Furthermore it is a filter for
    what should be visible to the agent. Also, it can potentially act as a
    filter on how actions are transmitted to the environment.

    Attributes:
      env (Environment): the environment instance.
      finished (bool): ?    '
      reward (int): the current reward of the simulation.
      status (int): ?
      cum_reward (int): the sum reward since the beginning of the episode.
      samples (int): number of steps in the current episode.
    """

    def __init__(
        self,
        window_size: int = 4,
        max_dist: int = 2,
        player_pos: int = 11,
        *args,
        **kwargs,
    ):
        """Constructor.

        Args:
          environment (Environment): the environment instance.
        """

        self.env = core.Environment(*args, **kwargs)
        self.window_size = window_size
        self.max_dist = max_dist
        self.player_pos = player_pos
        self.finished = False
        self.state = None
        self.status = 0
        self.cum_reward = 0
        self.samples = 0
        self.reward = {
            "status": 0,
            "distance": 0,
            "timeLeft": 0,
            "marioMode": 0,
            "coins": 0,
        }
        self._action_pool = np.array(
            [
                # [backward, forward, crouch, jump, speed/bombs]
                [0, 0, 0, 0, 0],  # do nothing
                [0, 0, 0, 1, 0],  # jump
                [0, 0, 0, 0, 1],  # bombs
                [0, 0, 1, 0, 0],  # crouch
                [0, 0, 1, 0, 1],  # crouch and bombs
                [0, 0, 0, 1, 1],  # jump and bombs/speed
                [0, 1, 0, 0, 0],  # move forward
                [0, 1, 0, 0, 1],  # move forward and bombs/speed
                [0, 1, 0, 1, 0],  # jump forward
                [0, 1, 0, 1, 1],  # jump forward and bombs/speed
                [1, 0, 0, 0, 0],  # move backward
                [1, 0, 0, 0, 1],  # move backward and bombs/speed
                [1, 0, 0, 1, 0],  # jump backward
                [1, 0, 0, 1, 1],  # jump backward and bombs/speed
            ]
        )
        self.objects = {
            "soft": [
                -11,
            ],
            "hard": [20, -10],
            "enemy": [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15],
            "brick": [16, 21],
            "projetil": [25],
        }

    def reset(self):
        """Reinitialize the environment."""

        self.env.reset()
        self.cum_reward = 0
        self.samples = 0
        self.finished = False
        self.status = 0
        self.reward = {
            "status": 0,
            "distance": 0,
            "timeLeft": 0,
            "marioMode": 0,
            "coins": 0,
        }

    def filter_actions(self) -> np.array:
        """This function filter the action pool"""
        action_pool = np.copy(self._action_pool)
        if not self.state["can_jump"]:
            action_pool = action_pool[action_pool[:, 3] == 0]
        return action_pool

    def disconnect(self):
        self.env.disconnect()

    def get_sensors(self):
        """Bridge to environment."""
        sense = self.env.get_sensors()
        self.state = self.build_state(sense)
        if len(sense) == self.env.fitness_values:
            reward_data = {
                "status": sense[0],
                "distance": sense[1],
                "timeLeft": sense[2],
                "marioMode": sense[3],
                "coins": sense[4],
            }
            self.reward = self.compute_reward(reward_data)
            self.status = sense[0]
            self.finished = True

        return self.state

    def compute_reward(self, reward_data):
        """Function that compute reward"""
        return reward_data

    def perform_action(self, action):
        """Bridge to environment."""

        if not self.finished:
            self.env.perform_action(action)
            self.cum_reward += self.reward["distance"]
            self.samples += 1

    def build_state(self, sense):
        """Build state from level scene"""
        state_vars = [
            "can_jump",
            "on_ground",
            "mario_floats",
            "enemies_floats",
            "level_scene",
        ]
        state = {}
        if len(sense) == 6:
            for var, value in zip(state_vars, sense[:5]):
                state[var] = value
            state["episode_over"] = False
        else:
            for var in state_vars:
                state[var] = None
            state["episode_over"] = True

        ground_pos = (
            self._get_ground(state["level_scene"], state["on_ground"])
            if not state["episode_over"]
            else None
        )

        for o_name, o_values in self.objects.items():
            for dist in range(1, self.max_dist + 1):
                state[f"{o_name}_{dist}"] = (
                    self._is_near(state["level_scene"], o_values, dist)
                    if not state["episode_over"]
                    else None
                )

        for dist in range(1, self.max_dist + 1):
            state[f"has_role_near_{dist}"] = (
                self._has_role(state["level_scene"], ground_pos, dist)
                if not state["episode_over"]
                else None
            )

        return state

    def _is_near(self, level_scene, objects, dist):
        for i in range(1, 4):
            x = max(0, self.player_pos - i)
            y = min(level_scene.shape[0], self.player_pos + dist)
            if level_scene[x, y] in objects:
                return True
        return False

    def _has_role(self, level_scene, ground_pos, dist):
        y = min(level_scene.shape[0], self.player_pos + dist)
        return (level_scene[ground_pos:, y] == 0).all()

    def _get_ground(self, level_scene, on_ground):
        start, end = 11 - self.window_size, 11 + self.window_size
        if on_ground:
            ground_pos = 12
        else:
            is_ground = (level_scene[start:, start:end] == -10) * 1
            is_ground = np.nonzero(is_ground)
            if is_ground[0].shape[0]:
                ground_pos = is_ground[0][0] + start
            else:
                ground_pos = 10
        return ground_pos
