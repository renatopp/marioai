import logging
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

from .utils import extractObservation

__all__ = ["Environment"]


class Environment(object):
    """Interface to the MarioAI simulator.

    Attributes:
      level_difficulty (int): the level difficulty. There is no limit, but it
        is suggested to be kept between 0 and 30. Defaults to 0.
      level_type (int): the level type, use 0 for overground; 1 for
        underground; 2 for castle; and 3 for random. Defaults to 0.
      creatures_enabled (bool): whether if creates are enabled or not, defaults
        to True.
      init_mario_mode (int): initial Mario mode; Use 0 for small; 1 for large;
        and 2 for large with fire. Defaults to 2.
      level_seed (int): the level randomization seed, defaults to 1.
      time_limit (int): the limit Marioseconds (which is faster than the
        actual seconds), defaults to 100.
      fast_tcp (bool): defaults to False.
      visualization (bool): whether the level visualization (on server) is on
        or off.
      custom_args (str): a string with custom arguments to the server.
      fitness_values (int): defaults to 5
      connected (bool): whether the environment is connected to the simulator
        or not.
    """

    def __init__(self, name="Unnamed agent", host="localhost", port=4242):
        """Constructor.

        Args:
          name (str): the bot's name, defaults to "Unnamed agent".
          host (str): the server address, defaults to "localhost".
          port (int): the server address, defaults to 4242.
        """
        self.level_difficulty = 0
        self.level_type = 0
        self.creatures_enabled = True
        self.init_mario_mode = 2
        self.level_seed = 1
        self.time_limit = 100
        self.fast_tcp = False

        self.visualization = True
        self.custom_args = ""
        self.fitness_values = 5

        self._server_process = None
        self._tcpclient = self._run_server(name, host, port)
        # self._tcpclient = TCPClient(name, host, port)
        # self._tcpclient.connect()

    def _check_java(self):
        try:
            print('Checking if Java is installed...')
            p = subprocess.Popen(['java', '-version'],
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT)
            out = list(iter(p.stdout.readline, b''))
            print(f"Java version: {out[0].decode('ascii')}")
        except FileNotFoundError:
            raise EnvironmentError('Java is not installed!')
        
    def _run_server(self, name, host, port):
        print(os.getcwd())
        self._check_java()
        source_path = Path(__file__).resolve()
        source_dir = source_path.parent
        self._server_process = subprocess.Popen(
            ["nohup", "java", "ch.idsia.scenarios.MainRun", "-server", "on"],
            cwd=source_dir / "server",
            stdout=open(
                source_dir / "server/tmp/server_logOut.log", "w", encoding="utf-8"
            ),
            stderr=open(
                source_dir / "server/tmp/server_logErr.log", "w", encoding="utf-8"
            ),
        )
        connections_attempts = 5
        attempt = 1
        game_is_down = True
        while game_is_down:
            try:
                print(f"Connection attempt: {attempt}/{connections_attempts}")
                client = TCPClient(name, host, port)
                client.connect()
                game_is_down = False
                return client
            except ConnectionRefusedError as e:  # pylint: disable=invalid-name
                if attempt == connections_attempts:
                    raise e
                attempt += 1
                time.sleep(5)

    @property
    def connected(self):
        return self._tcpclient.connected

    def disconnect(self):
        self._tcpclient.disconnect()
        self._server_process.kill()

    def get_sensors(self):
        """Receives an observation from the simulator.

        Returns:
          A list with the observation values. See agent.
        """
        data = self._tcpclient.recvData()

        if data == "ciao":
            self._tcpclient.disconnect()

        elif len(data) > 5:
            return extractObservation(data)

        else:
            logging.warning(f"[ENVIRONMENT] Unexpected received data: {data}")
            raise EnvironmentError('Unexpected received data from server')

    def perform_action(self, action):
        """Takes a numpy array of ints and sends as a string to server.

        Each position of the array represents a different action, use 1 to
        enable an action and 0 to disable it:

            [backward, forward, crouch, jump, speed/bombs]

        Example:

            # send mario to the right
            env.perform_action([0, 1, 0, 0, 0])

            # jump backward
            env.perform_action([1, 0, 0, 1, 0])

        Args:
          action (list): a list of integers.
        """

        action_str = ""
        for i in range(5):
            if action[i] == 1:
                action_str += "1"

            elif action[i] == 0:
                action_str += "0"

            else:
                raise ValueError("something very dangerous happen....")

        action_str += "\r\n"
        self._tcpclient.send_data(str.encode(action_str))

    def reset(self):
        """Resets the simulator and configure it according to the variables set
        here."""

        argstring = f"-ld {self.level_difficulty} -lt {self.level_type} -mm {self.init_mario_mode} -ls {self.level_seed} -tl {self.time_limit} "
        if self.creatures_enabled:
            argstring += "-pw off "
        else:
            argstring += "-pw on "

        if self.visualization:
            argstring += "-vis on "
        else:
            argstring += "-vis off "

        if self.fast_tcp:
            argstring += "-fastTCP on"
        self._tcpclient.send_data(
            str.encode("reset -maxFPS on " + argstring + self.custom_args + "\r\n")
        )


class TCPClient(object):
    """A simple client for the marioai TCP server.

    Attributes:
      name (str): the bot's name.
      host (str): the server address.
      port (int): the server port.
      sock (Socket): the socket object.
      connected (bool): whether the client is connected or not.
      buffer_size (int): the buffer size.
    """

    def __init__(self, name="", host="localhost", port=4242):
        """Constructor.

        Args:
          name (str): the bot's name.
          host (str): the server address, defaults to "localhost".
          port (int): the server address, defaults to 4242.
        """

        self.name = name
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        self.buffer_size = 4096

    def __del__(self):
        """Destructor."""

        self.disconnect()

    def connect(self):
        """Connects to the provided address."""

        h, p = self.host, self.port

        logging.info(f"[TCPClient] trying to connect to {h}:{p}")
        self.sock = socket.socket()

        self.sock.connect((h, p))
        logging.info(f"[TCPClient] connection to {h}:{p} succeeded")

        data = self.recvData()
        logging.info(f"[TCPClient] greetings received: {data}")

        message = f"Client: Dear Server, hello! I am {self.name}\r\n"
        self.send_data(str.encode(message))

        self.connected = True

    def disconnect(self):
        """Disconnects from the server."""

        self.sock.close()
        self.connected = False
        logging.info("[TCPClient] client disconnected")

    def recvData(self):
        """Receives data from server.

        Returns:
          The received string data.
        """

        try:
            return self.sock.recv(self.buffer_size)

        except socket.error as message:
            logging.error(f"[TCPClient] error while receiving. Message: {message}")
            raise socket.error

    def send_data(self, data):
        """Send data to server.

        Args:
          data (str): the string to be sent.
        """

        try:
            self.sock.send(data)

        except socket.error as message:

            logging.error(f"[TCPClient] error while sending. Message: {message}")
            raise OSError(f"[TCPClient] error while sending. Message: {message}")
