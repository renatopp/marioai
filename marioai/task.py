
import marioai

__all__ = ['Task']


class Task(object):
    '''A task handles communication with the environment.

    It decides how to evaluate the observations, potentially returning 
    reinforcement rewards or fitness values. Furthermore it is a filter for 
    what should be visible to the agent. Also, it can potentially act as a 
    filter on how actions are transmitted to the environment.

    Attributes:
      env (Environment): the environment instance.
      finished (bool): ?
      reward (int): the current reward of the simulation.
      status (int): ?
      cum_reward (int): the sum reward since the beginning of the episode.
      samples (int): number of steps in the current episode.
    '''

    def __init__(self, *args, **kwargs):
        '''Constructor.

        Args:
          environment (Environment): the environment instance.
        '''

        self.env = marioai.Environment(*args, **kwargs)
        self.finished = False
        self.reward = 0
        self.status = 0
        self.cum_reward = 0
        self.samples = 0

    def reset(self):
        '''Reinitialize the environment.'''

        self.env.reset()
        self.cum_reward = 0
        self.samples = 0
        self.finished = False
        self.reward = 0
        self.status = 0

    def get_sensors(self): 
        '''Bridge to environment.'''

        sense = self.env.get_sensors()
        if len(sense) == self.env.fitness_values:
            self.reward = sense[1]
            self.status = sense[0]
            self.finished = True

        return sense

    def perform_action(self, action):
        '''Bridge to environment.'''

        if not self.finished:
            self.env.perform_action(action)
            self.cum_reward += self.reward
            self.samples += 1

