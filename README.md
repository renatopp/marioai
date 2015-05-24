# MARIOAI

This repository is a python focused base for the Mario AI tool. All original code can be found in:

  http://julian.togelius.com/mariocompetition2009/


## Server configuration

Note: you need java installed and configured in your computer in order to run the server.

Whether execute the `server.bat` or use the following command inside the server directory:

    java ch.idsia.scenarios.MainRun -server on


## Marking a python bot

The original code provided by Togelius were simplified and can be found in `marioai` package. Now, you can simply inherit the `marioai.Agent` class and implement its methods. Use the following boilerplate:

    class MyAgent(marioai.Agent):
        def sense(self, obs):
            super(MyAgent, self).sense(obs)

        def act(self):
            return [0, 0, 0, 0, 0]

        def giveRewards(self, reward, cum_reward):
            pass


### Sensorial information

By default, the base agent store the following sensorial information:

- **can_jump**: a boolean attribute that tells if the agent can jump or not.
- **on_ground**: tells if the agents is touching the ground or not.
- **mario_floats**: the Mario position on the level.
- **enemies_floats**: the enemies position on the level.
- **level_scene**: a 22x22 numpy array containing the elements of the level aroung the agent (Mario is at [11, 11]).

| **Value** | **Meaning**                                           |
| --------- | ----------------------------------------------------- |
| -11       | soft obstacle, can jump through                       |
| -10       | hard obstacle, cannot pass through                    |
| 0         | no obstacle or enemy                                  |
| 1         | mario                                                 |
| 2         | Enemy goomba                                          |
| 3         | Enemy goomba winged                                   |
| 4         | Enemy red koopa                                       |
| 5         | Enemy red koopa winged                                |
| 6         | Enemy green koopa                                     |
| 7         | Enemy green koopa winged                              |
| 8         | Enemy bullet bill                                     |
| 9         | Enemy spiky                                           |
| 10        | Enemy spiky winged                                    |
| 12        | Enemy flower                                          |
| 13        | Enemy shell                                           |
| 14        | mushroom                                              |
| 15        | fire_flower                                           |
| 16        | brick (simple/with coin/with mushroom/with flower)    |
| 20        | enemy obstacle (ex.: flower pot or parts of a cannon) |
| 21        | question brick (with a coin or mushroom/flower)       |
| 25        | mario weapon projectile                               |
| 42        | undefined                                             |


### Control signals

Each position of the array represents a different action, use 1 to
enable an action and 0 to disable it:

    [backward, forward, crouch, jump, speed/bombs]

Example:

    # send the agent to the right
    def act(self):
        return [0, 1, 0, 0, 0]

    # jump backward
    def act(self):
        return [1, 0, 0, 1, 0]