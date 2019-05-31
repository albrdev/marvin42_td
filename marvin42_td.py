#!/usr/bin/env python3

"""
@author: albrdev
@email: albrdev@gmail.com
@date: 2019-05-13
"""

import sys, time, argparse, configparser, signal

from modules.pathtools import *
from modules.daemon import Daemon
from receiver import Receiver

class marvin42_td(Daemon):
    """
    marvin42 Transmission Daemon
    Listens for incomming (motor) commands and executes them
    """
    __slots__ = ['server']

    def init(self):
        super(marvin42_td, self).init()

        # Using the Receiver class
        self.server = Receiver((config['server']['bind_address'], int(config['server']['bind_port'])), int(config['server']['max_connections']))

    def signal_handler(self, num, frame):
        """
        Signal handler
        """
        {
            signal.SIGINT: lambda: sys.exit(0), 
            signal.SIGTERM: lambda: sys.exit(0),
            signal.SIGHUP: lambda: self.restart()
        }.get(num, lambda *args: None)()

    def run(self):
        """
        Overriden daemon main loop
        Lets the server check and handle connections and data
        """
        self.server.poll()
        time.sleep(0.1)

if __name__ == '__main__':
    global config

    if len(sys.argv) < 2:
        print ("Usage: {app} start|stop|restart".format(app=sys.argv[0]))
        sys.exit(1)

    args = argparse.ArgumentParser(
        description="marvin42 transmission daemon",
        epilog="marvin42, 2019"
    )

    args.add_argument('operation', type=str, help="Operation to perform", metavar='operation')
    args.add_argument('-c', '--config', dest='config', action=FullPath, type=str, default=pathtools.fullpath('/etc/marvin42_tdrc'), help="Custom config file (optional)", metavar='filepath')
    args = args.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    daemon = marvin42_td(config['daemon']['user'], config['daemon']['pid_file'], config['daemon']['log_default'], config['daemon']['log_error'])
    if args.operation == 'start':
        daemon.start()
    elif args.operation == 'stop':
        daemon.stop()
    elif args.operation == 'restart':
        daemon.restart()
    else:
        print ("Unknown operation \'{op}\'".format(op=sys.argv[1]))
        sys.exit(1)
