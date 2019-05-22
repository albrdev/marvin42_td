#!/usr/bin/env python3

import sys, time, math, argparse, configparser, signal, socket, struct
from typing import TypeVar
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B
from ev3dev2.sensor.lego import InfraredSensor
from ev3dev2.sensor import INPUT_1, INPUT_2
from ev3dev2 import DeviceNotFound

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

class marvin42_cgd(Daemon):
    __slots__ = ['IR_SENSOR_MAXRANGE_CM', 'HEADER_MOTORSTOP', 'ir_sensor_front', 'ir_sensor_back', 'motor_pair']

    def init(self):
        super(marvin42_cgd, self).init()

        # WHen using 'proximity' property of 'InfraredSensor', the documentation states this:
        # "An estimate of the distance between the sensor and objects in front of it, as a percentage. 100% is approximately 70cm/27in."
        # https://python-ev3dev.readthedocs.io/en/ev3dev-stretch/sensors.html#infrared-sensor
        self.IR_SENSOR_MAXRANGE_CM = 70
        self.HEADER_MOTORSTOP = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSTOP), 0)

        try:
            self.ir_sensor_front = InfraredSensor(INPUT_1)
        except DeviceNotFound:
            self.ir_sensor_front = None

        try:
            self.ir_sensor_back = InfraredSensor(INPUT_2)
        except DeviceNotFound:
            self.ir_sensor_back = None

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
        threshold_front = float(config.get('motor', 'autostop_threshold_front', fallback=50.0))
        threshold_back = float(config.get('motor', 'autostop_threshold_back', fallback=50.0))

        if threshold_front > 0 and self.ir_sensor_front is not None:
            distance = (self.ir_sensor_front.proximity / 100) * self.IR_SENSOR_MAXRANGE_CM
            if distance <= threshold_front and self.motor_pair.speed > 0:
                print("Obstacle detected {d:0.2f}cm ahead (Threshold: {t}). Sending stop command".format(d=distance, t=threshold_front))
                self.send_packet_motorstop((config['remote']['bind_address'], int(config['remote']['bind_port'])))
                return

        if threshold_back > 0 and self.ir_sensor_back is not None:
            distance = (self.ir_sensor_back.proximity / 100) * self.IR_SENSOR_MAXRANGE_CM
            if distance <= threshold_back and self.motor_pair.speed < 0:
                print("Obstacle detected {d:0.2f}cm behind (Threshold: {t}). Sending stop command".format(d=distance, t=threshold_back))
                self.send_packet_motorstop((config['remote']['bind_address'], int(config['remote']['bind_port'])))
                return

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

    daemon = marvin42_cgd(config['daemon']['user'], config['daemon']['pid_file'], config['daemon']['log_default'], config['daemon']['log_error'])
    if args.operation == 'start':
        daemon.start()
    elif args.operation == 'stop':
        daemon.stop()
    elif args.operation == 'restart':
        daemon.restart()
    else:
        print ("Unknown operation \'{op}\'".format(op=sys.argv[1]))
        sys.exit(1)
