# pylint: disable=logging-fstring-interpolation
import marioai
import marioai.agents as agents
import marioai.core as core
import logging

logger = logging.getLogger(__name__)


def main():
    task = core.Task(max_dist=4)
    mc_model = agents.MonteCarloAgent(100, 0.9, min_epsilon=0.3, reward_threshold=2, reward_increment=0.5)
    mc_model = mc_model.fit(task=task, level_difficult=0, mario_mode=0, time_limit=100, response_delay=0, max_fps=720)

if __name__ == '__main__':
    main()