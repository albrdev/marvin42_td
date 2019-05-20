#!/usr/bin/env python3

import sys, time, argparse, configparser, signal, socket, struct
from ev3dev2.sensor.lego import InfraredSensor

from modules.pathtools import *
from modules.daemon import Daemon
from modules.networking import PacketHeader
from modules.marvin42 import *

class marvin42_cgd(Daemon):
    __slots__ = ['HEADER_MOTORSTOP', 'config', 'ir_sensor']

    def __init__(self, args, config):
        self.HEADER_MOTORSTOP = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSTOP), 0)
        self.config = config

        super(marvin42_cgd, self).__init__(main_config['daemon']['user'], main_config['daemon']['pid_file'], main_config['daemon']['log_default'], main_config['daemon']['log_error'])

        
        self.ir_sensor = InfraredSensor()

    def signal_handler(self, num, frame):
        {
            signal.SIGINT: lambda: sys.exit(0), 
            signal.SIGTERM: lambda: sys.exit(0),
            signal.SIGHUP: lambda: self.restart()
        }.get(num, lambda *args: None)()

    def send_packet_motorstop(host: tuple, timeout: float = 5):
        s = socket.socket()
        s.settimeout(timeout)

        s.connect(host)
        s.send(self.HEADER_MOTORSTOP)

    def run(self):
        if self.ir_sensor.value() < config.get('motor', 'autostop_threshold', fallback=50):
            send_packet_motorstop((config['server']['bind_address'], int(config['server']['bind_port'])))

        time.sleep(0.25)

if __name__ == '__main__':
    global args
    global config

    args = argparse.ArgumentParser(
        description="marvin42 collision guard daemon",
        epilog="marvin42, 2019"
    )

    args.add_argument('operation', type=str, help="Operation to perform", metavar='operation')
    args.add_argument('-c', '--config', dest='config', action=FullPath, type=str, default=pathtools.fullpath('/etc/marvin42_cgdrc'), help="Custom config file (optional)", metavar='filepath')
    args = args.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    daemon = marvin42_cgd(args, config)
    if args.operation == 'start':
        daemon.start()
    elif args.operation == 'stop':
        daemon.stop()
    elif args.operation == 'restart':
        daemon.restart()
    else:
        print ("Unknown operation \'{op}\'".format(op=sys.argv[1]))
        sys.exit(1)
