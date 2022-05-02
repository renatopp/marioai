import time
import os
import signal
import subprocess
import logging

__all__ = ["Experiment"]


class Experiment(object):
    """Episodic Experiment"""

    def __init__(self, task, agent, response_delay=0):
        self.response_delay = response_delay
        self._frame = 0
        self.task = task
        self.agent = agent
        self.max_fps = -1
        self.action = 0
    def _step(self):
        state = self.task.get_sensors()
        if self.task.finished or (self._frame % (self.response_delay + 1)) == 0:
            self.agent.sense(state)
            self.task.perform_action(self.agent.act())
            self.agent.give_rewards(self.task.reward, self.task.cum_reward)
        else:
            self.task.perform_action([0, 0, 0, 0, 0])
        self._frame += 1
        return self.task.reward

    def _episode(self):
        rewards = []

        self.agent.reset()
        self.task.reset()
        while not self.task.finished:
            r = self._step()
            rewards.append(r)

            if self.max_fps > 0:
                time.sleep(1.0 / self.max_fps)

        return rewards

    def do_episodes(self, n=1):
        rewards = []

        for _ in range(n):
            rewards.append(self._episode())
        return rewards
