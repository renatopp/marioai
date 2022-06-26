import time
from grpc import Status
import gym
from gym import spaces
import numpy as np
from ..core import Environment

__all__ = ["MarioEnv"]

ACTIONS = [
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

LEVEL_SHAPE = (22, 22)

PLAYER_POSITION = 11

class MarioEnv(gym.Env):

    def __init__(
        self,
        level_difficult: int = 0,
        level_type: int = 0,
        creatures_enabled: bool = True,
        mario_mode: int = 2,
        level_seed: int = 1,
        time_limit: int = 100,
        max_fps: int = 24,
        visualization: bool = True,
        fitness_values: int = 5,):
        self._env = Environment()
        self.max_fps = max_fps
        """
        self.observation_space = spaces.Dict(
            {
                "level_scene": spaces.Box(low=0, high=26, shape=LEVEL_SHAPE),
                "can_jump": spaces.Discrete(2),
                "on_ground": spaces.Discrete(2),
            }
        )
        """
        self.observation_space = spaces.Box(low=0, high=26, shape=LEVEL_SHAPE)
        self.action_space = spaces.Discrete(len(ACTIONS))
        self.mario_pos = 0
        self.finished = False
        self.last_sense = None

        self._env.level_difficulty = level_difficult
        self._env.level_type = level_type
        self._env.creatures_enabled = creatures_enabled
        self._env.init_mario_mode = mario_mode
        self._env.level_seed = level_seed
        self._env.time_limit = time_limit
        self._env.visualization = visualization
        self._env.fitness_values = fitness_values

    def _get_info(self, sense):
        if len(sense) == 6:
            return {"distance": sense[2][0]}
        else:
            return {"distance": sense[1]}

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
                if var == "level_scene":
                    value[value == 25] = 22
                    value[value == -11] = 23
                    value[value == -10] = 24
                    value[value == 42] = 25
                    value[PLAYER_POSITION, PLAYER_POSITION] = 26
                state[var] = value
        else:
            for var in state_vars:
                state[var] = 0
            self.finished = True
            state["level_scene"] = np.zeros(LEVEL_SHAPE)


        return state

    def reset(self):
        self._env.reset()
        sense = self._env.get_sensors()
        self.finished = False
        #self._env.perform_action(ACTIONS[0])
        observation = {
                "level_scene": np.zeros(LEVEL_SHAPE),
                "can_jump": 0,
                "on_ground": 0,
            }
        return observation["level_scene"]


    def step(self, action):
        self._env.perform_action(ACTIONS[action])
        sense = self._env.get_sensors()
        observation = self.build_state(sense)
        info = self._get_info(sense)
        if self.finished:
            reward_data = {
                "status": sense[0],
                "distance": sense[1],
                "timeLeft": sense[2],
                "marioMode": sense[3],
                "coins": sense[4],
            }
            reward = self.compute_reward(reward_data)
        else:
            reward = self.compute_reward(observation)
        return observation["level_scene"], reward, self.finished, info

    def compute_reward(self, reward_data):
        """Function that compute reward"""
        if "distance" in reward_data:
            return reward_data["distance"]
        return 0

    def close(self):
        self._env.disconnect()