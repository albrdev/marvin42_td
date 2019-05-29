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
    """
    Helper class for speed calculation (currently supports large motors only)
    """
    __slots__ = ['motor_a', 'motor_b']

    def __init__(self, output_a, output_b):
        self.motor_a = LargeMotor(output_a)
        self.motor_b = LargeMotor(output_b)

    @property
    def speed_a(self):
        """
        Return the current speed of motor A (in percentage)
        """
        return self.motor_a.speed / self.motor_a.max_speed

    @property
    def speed_b(self):
        """
        Return the current speed of motor B (in percentage)
        """
        return self.motor_b.speed / self.motor_b.max_speed
        
    @property
    def speed(self):
        """
        Return the current speed of both motors (mean value) (in percentage)
        """
        return (self.speed_a + self.speed_b) / 2

class marvin42_cgd(Daemon):
    """
    marvin42 Collision Guard Daemon
    Detecting and manages collision handling using infrared distance sensors
    """
    __slots__ = ['IR_SENSOR_MAXRANGE_CM', 'HEADER_MOTORSTOP', 'ir_sensor_front', 'ir_sensor_back', 'motor_pair']

    def init(self):
        super(marvin42_cgd, self).init()

        # WHen using 'proximity' property of 'InfraredSensor', the documentation states this:
        # "An estimate of the distance between the sensor and objects in front of it, as a percentage. 100% is approximately 70cm/27in."
        # https://python-ev3dev.readthedocs.io/en/ev3dev-stretch/sensors.html#infrared-sensor
        self.IR_SENSOR_MAXRANGE_CM = 70
        self.HEADER_MOTORSTOP = struct.pack(PacketHeader.FORMAT, int(CommandID.MOTORSTOP), 0)

        # Sensors are optional and should not crash the application if the do not exist
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
        """
        Signal handler
        """
        {
            signal.SIGINT: lambda: sys.exit(0), 
            signal.SIGTERM: lambda: sys.exit(0),
            signal.SIGHUP: lambda: self.restart()
        }.get(num, lambda *args: None)()

    AnyNum = TypeVar('AnyNum', int, float) # float OR int types
    def send_packet_motorstop(self, host: tuple, timeout: AnyNum = 5):
        """
        Sends a simple motor stop command to the transmission daemon
        """
        s = socket.socket()
        s.settimeout(timeout)

        s.connect(host)
        s.send(self.HEADER_MOTORSTOP)

    def run(self):
        """
        Overriden daemon main loop
        Reads IR sensors and handles promixity actions
        """
        # Handle sensor A (front)
        threshold_front = float(config.get('motor', 'autostop_threshold_front', fallback=25.0)) # Read threshold value from config
        if threshold_front > 0 and self.ir_sensor_front is not None: # Only if threshold is a 'valid' value and sensor is plugged in
            distance = (self.ir_sensor_front.proximity / 100) * self.IR_SENSOR_MAXRANGE_CM # Calculate actual distance
            if distance <= threshold_front and self.motor_pair.speed > 0: # If actual distance if within threshold value and the motor is currently running forwards
                print("Obstacle detected {d:0.2f}cm ahead (Threshold: {t}). Sending stop command".format(d=distance, t=threshold_front))
                self.send_packet_motorstop((config['remote']['bind_address'], int(config['remote']['bind_port']))) # Send motor stop
                return

        # Same princial as above, but with sensor B (back)
        threshold_back = float(config.get('motor', 'autostop_threshold_back', fallback=15.0))
        if threshold_back > 0 and self.ir_sensor_back is not None:
            distance = (self.ir_sensor_back.proximity / 100) * self.IR_SENSOR_MAXRANGE_CM
            if distance <= threshold_back and self.motor_pair.speed < 0: # The deiffernece here is that we check if the motor is running backwards instead
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
