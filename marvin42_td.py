#!/usr/bin/env python3

import sys, time, argparse, configparser, signal

from modules.pathtools import *
from modules.daemon import Daemon
from .receiver import Receiver

class marvin42_td(Daemon):
    def __init__(self, args, config):
        super().__init__(config['daemon']['user'], config['daemon']['pid_file'], config['daemon']['log_default'], config['daemon']['log_error'])

        self.server = Receiver((config['server']['bind_address'], int(config['server']['bind_port'])), int(config['server']['max_connections']))

    def handle_signals(self, num, frame):
        {
            signal.SIGINT: lambda: sys.exit(0), 
            signal.SIGTERM: lambda: sys.exit(0)
        }.get(num, lambda *args: None)()

    def run(self):
        self.server.poll()
        time.sleep(0.1)

if __name__ == '__main__':
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

    daemon = marvin42_td(args, config)
    if args.operation == 'start':
        daemon.start()
    elif args.operation == 'stop':
        daemon.stop()
    elif args.operation == 'restart':
        daemon.restart()
    else:
        print ("Unknown operation \'{op}\'".format(op=sys.argv[1]))
        sys.exit(1)
