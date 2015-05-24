import sys
import socket
import logging
import time

from marioai.utils import extractObservation

__all__ = ['Environment']

class Environment(object):
    '''Interface to the MarioAI simulator.

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
    '''

    def __init__(self, name='Unnamed agent', host='localhost', port=4242):
        '''Constructor.

        Args:
          name (str): the bot's name, defaults to "Unnamed agent".
          host (str): the server address, defaults to "localhost".
          port (int): the server address, defaults to 4242.
        '''
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

        self._tcpclient = TCPClient(name, host, port)
        self._tcpclient.connect()


    @property
    def connected(self):
        return self._tcpclient.connected


    def get_sensors(self):
        '''Receives an observation from the simulator.

        Returns:
          A list with the observation values. See agent.
        '''

        data = self._tcpclient.recvData()

        if data == 'ciao':
            self._tcpclient.disconnect()

        elif len(data) > 5:
            return extractObservation(data)

        else:
            logging.warning('[ENVIRONMENT] Unexpected received data: %s'%data);


    def perform_action(self, action):
        ''' Takes a numpy array of ints and sends as a string to server.

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
        '''
        
        actionStr = ""
        for i in xrange(5):
            if action[i] == 1:
                actionStr += '1'

            elif action[i] == 0:
                actionStr += '0'

            else:
                raise "something very dangerous happen...."

        actionStr += "\r\n"
        self._tcpclient.sendData(actionStr)
    

    def reset(self):
        '''Resets the simulator and configure it according to the variables set
        here.'''

        argstring = "-ld %d -lt %d -mm %d -ls %d -tl %d "%(self.level_difficulty,
                                                           self.level_type,
                                                           self.init_mario_mode,
                                                           self.level_seed,
                                                           self.time_limit)
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

        self._tcpclient.sendData("reset -maxFPS on "+argstring + self.custom_args+"\r\n")





class TCPClient(object):
    '''A simple client for the marioai TCP server.
    
    Attributes:
      name (str): the bot's name.
      host (str): the server address.
      port (int): the server port.
      sock (Socket): the socket object.
      connected (bool): whether the client is connected or not.
      buffer_size (int): the buffer size.
    '''

    def __init__(self, name='', host='localhost', port=4242):
        '''Constructor.

        Args:
          name (str): the bot's name.
          host (str): the server address, defaults to "localhost".
          port (int): the server address, defaults to 4242.
        '''

        self.name = name
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False;
        self.buffer_size = 4096

    def __del__(self):
        '''Destructor.'''

        self.disconnect()

    def connect(self):
        '''Connects to the provided address.'''

        h, p = self.host, self.port

        logging.info('[TCPClient] trying to connect to %s:%s'%(h, p))
        self.sock = socket.socket()

        try:
            self.sock.connect((h, p))
            logging.info('[TCPClient] connection to %s:%s succeeded'%(h, p))

            data = self.recvData()
            logging.info('[TCPClient] greetings received: %s'%data)

        except socket.error, message:
            logging.error('[TCPClient] connection error: %s'%message[1])
            sys.exit(1)

        message = 'Client: Dear Server, hello! I am %s\r\n'%self.name
        self.sendData(message)

        self.connected = True;

    def disconnect(self):
        '''Disconnects from the server.'''

        self.sock.close()
        self.connected = False
        logging.info('[TCPClient] client disconnected')

    def recvData(self):
        '''Receives data from server.

        Returns:
          The received string data.
        '''

        try:
            return self.sock.recv(self.buffer_size)

        except socket.error, message:
            logging.error('[TCPClient] error while receiving. Message: %s'%message)
            raise socket.error

    def sendData(self, data):
        '''Send data to server.

        Args:
          data (str): the string to be sent.
        '''
        try:
            self.sock.send(data)

        except socket.error, message:
            logging.error('[TCPClient] error while sending. Message: %s'%message)
            raise socket.error


