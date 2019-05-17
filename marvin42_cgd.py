#!/usr/bin/env python3

import sys, time, argparse, configparser, signal, socket, struct
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, MoveTank
from ev3dev2.sensor.lego import InfraredSensor

from modules.pathtools import *
from modules.daemon import Daemon
from modules.networking import PacketHeader
from modules.marvin42 import *

header = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSTOP), 0)

motorPair = MoveTank(OUTPUT_A, OUTPUT_B)
irSensor = InfraredSensor()

def send_packet_motorstop(host: tuple, timeout: float = 5):
    s = socket.socket()
    s.settimeout(timeout)

    s.connect(host)
    s.send(header)
    if data is not None:
        s.send(data)

def monitor():
    while True:
        if ir.value() < config.get('motor', 'autostop_threshold', fallback=50):
            send_packet_motorstop(('localhost', int(config['server']['bind_port'])))

        time.sleep(0.25)

def signal_handler(self, num, frame):
    if num == signal.SIGHUP:
        config.read(args.config)

if __name__ == '__main__':
    global args
    global config

    args = argparse.ArgumentParser(
        description="marvin42 collision guard daemon",
        epilog="marvin42, 2019"
    )

    args.add_argument('-c', '--config', dest='config', action=FullPath, type=str, default=pathtools.fullpath('/etc/marvin42_tdrc'), help="Custom config file (optional)", metavar='filepath')
    args = args.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    signal.signal(signal.SIGHUP, self.handle_signals)

    try:
        moinitor()
    except KeyboardInterrupt:
        pass

    sys.exit()
