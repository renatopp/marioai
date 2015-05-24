
__all__ = ['Agent']

class Agent(object):
    '''Base class for an autonomous agent.

    Attributes:
      level_scene (list): a 22x22 numpy array containing the elements of the 
        level, including blocks and enemies.
      on_ground (bool): whether Mario is on ground or not.
      can_jump (bool): whether Mario can jump or not.
      mario_floats (list): 2-tuple with mario position.
      enemies_floats (list): list of 2-tuples with enimies_positions.
      episode_over (bool): whether the episode is over or not.
    '''

    def __init__(self):
        '''Contructor.'''
        self.level_scene = None
        self.on_ground = None
        self.can_jump = None
        self.mario_floats = None
        self.enemies_floats = None
        self.episode_over = False

    def reset(self):
        '''New episode.'''

        self.episode_over = False;

    def sense(self, obs):
        '''Receive sense.'''

        if len(obs) != 6:
            self.episode_over = True
        else:
            self.can_jump = obs[0]
            self.on_ground = obs[1]
            self.mario_floats = obs[2]
            self.enemies_floats = obs[3]
            self.level_scene = obs[4]

    def act(self):
        '''Return an action.'''
        pass

    def give_rewards(self, reward, cum_reward):
        '''Register current reward.'''
        pass