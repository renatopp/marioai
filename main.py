# pylint: disable=logging-fstring-interpolation
import marioai
import agents
import os
import signal
import subprocess
import time
import logging

logger = logging.getLogger(__name__)

def _run_server() -> subprocess.Popen:
    p = subprocess.Popen(
        ['java', 'ch.idsia.scenarios.MainRun', '-server', 'on'],
        stdout=open('/tmp/logOut.log', 'w'),
        stderr=open('/tmp/logErr.log', 'w'),
        cwd="./server"
    )
    return p

def main():
    logger.info("Starting server...")
    server_process = _run_server()
    connections_attempts = 5
    attempt = 1
    game_is_down = True
    while game_is_down:
        try:
            print(f"Connection attempt: {attempt}/{connections_attempts}")
            agent = agents.BaseAgent()
            task = marioai.Task()
            exp = marioai.Experiment(task, agent)
            print("Connection successfully established!")
            exp.max_fps = 24
            task.env.level_type = 0
            exp.doEpisodes()
            game_is_down = False

        except ConnectionRefusedError as e: # pylint: disable=invalid-name
            if attempt == connections_attempts:
                raise e
            attempt += 1
            time.sleep(1)

    os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
if __name__ == '__main__':
    main()