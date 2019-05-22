#!/usr/bin/env python3

import sys, time, math, argparse, configparser, signal, socket, struct
from typing import TypeVar
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B
from ev3dev2.sensor.lego import InfraredSensor

from modules.pathtools import *
from modules.daemon import Daemon
from modules.networking import PacketHeader
from modules.marvin42 import *

class MotorPair(object):
    __slots__ = ['motor_a', 'motor_b']

    def __init__(self, output_a, output_b):
        self.motor_a = LargeMotor(output_a)
        self.motor_b = LargeMotor(output_b)

    @property
    def speed_a(self):
        return self.motor_a.speed / self.motor_a.max_speed

    @property
    def speed_b(self):
        return self.motor_b.speed / self.motor_b.max_speed
        
    @property
    def speed(self):
        return (self.speed_a + self.speed_b) / 2

    @property
    def blaval(self, motor) -> float:
        p = (2.25 * math.pi) / 100
        revs_per_meter = 1 / p
        return revs.per_meter * self.motor.count_per_rot

    @property
    def speed_ms_a(self):
        count_per_meter = self.blaval(motor_a)
        return self.motor_a.speed / count_per_meter

    @property
    def speed_ms_b(self):
        count_per_meter = self.blaval(motor_b)
        return self.motor_b.speed / count_per_meter

    @property
    def speed_ms(self):
        return (self.speed_ms_a + self.speed_ms_b) / 2

class marvin42_cgd(Daemon):
    __slots__ = ['HEADER_MOTORSTOP', 'ir_sensor', 'motor_pair']

    def __init__(self):
        super(marvin42_cgd, self).__init__(config['daemon']['user'], config['daemon']['pid_file'], config['daemon']['log_default'], config['daemon']['log_error'])

        self.HEADER_MOTORSTOP = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSTOP), 0)
        self.ir_sensor = InfraredSensor()
        self.motor_pair = MotorPair(OUTPUT_A, OUTPUT_B)

    def signal_handler(self, num, frame):
        {
            signal.SIGINT: lambda: sys.exit(0), 
            signal.SIGTERM: lambda: sys.exit(0),
            signal.SIGHUP: lambda: self.restart()
        }.get(num, lambda *args: None)()

    AnyNum = TypeVar('AnyNum', int, float)
    def send_packet_motorstop(self, host: tuple, timeout: AnyNum = 5):
        s = socket.socket()
        s.settimeout(timeout)

        s.connect(host)
        s.send(self.HEADER_MOTORSTOP)

    def run(self):
        print("Speed: {0}, {1}".format(self.motor_pair.speed, self.motor_pair.speed_ms))
        threshold = int(config.get('motor', 'autostop_threshold', fallback=50))
        distance = self.ir_sensor.value()
        if distance <= threshold:
            print("Obstacle detected {d}cm ahead (Threshold: {t}). Sending stop command".format(d=distance, t=threshold))
            self.send_packet_motorstop((config['remote']['bind_address'], int(config['remote']['bind_port'])))

        time.sleep(0.25)

if __name__ == '__main__':
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

    daemon = marvin42_cgd()
    if args.operation == 'start':
        daemon.start()
    elif args.operation == 'stop':
        daemon.stop()
    elif args.operation == 'restart':
        daemon.restart()
    else:
        print ("Unknown operation \'{op}\'".format(op=sys.argv[1]))
        sys.exit(1)
