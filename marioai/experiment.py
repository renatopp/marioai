import time

__all__ = ['Experiment']

class Experiment(object):
    '''Episodic Experiment'''
    
    def __init__(self, task, agent):
        self.task = task
        self.agent = agent
        self.max_fps = -1

    def _step(self):
        self.agent.sense(self.task.get_sensors())
        self.task.perform_action(self.agent.act())
        self.agent.give_rewards(self.task.reward, self.task.cum_reward)
        return self.task.reward
    
    def _episode(self):
        rewards = []

        self.agent.reset()
        self.task.reset()
        while not self.task.finished:
            start_time = time.time()
            r = self._step()
            rewards.append(r)

            if self.max_fps > 0:
                time.sleep(start_time + 1./self.max_fps - time.time())

        return rewards

    def doEpisodes(self, n=1):
        rewards = []

        for _ in xrange(n):
            rewards.append(self._episode())

        return rewards