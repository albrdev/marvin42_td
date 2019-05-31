#!/usr/bin/env python3

"""
@author: albrdev
@email: albrdev@gmail.com
@date: 2019-05-13
"""

import sys, os, argparse, configparser, struct, subprocess
from modules.pathtools import *
from modules.networking import PacketReceiver, PacketHeader
from modules.marvin42 import *
import motor_control

class Receiver(PacketReceiver):
    """
    Custom defined class for socket connection and data handling
    """
    def on_client_connected(self, host: tuple):
        """
        Called when a new client connects
        """
        print("Server: Client connected: {h}".format(h=host))

    def on_client_disconnected(self, host: tuple):
        """
        Called when a client disconnects
        """
        print("Server: Client disconnected: {h}".format(h=host))

    def on_data_received(self, header: PacketHeader, data: bytes) -> bool:
        """
        Called when data has been completly received
        """
        print("Server: Data received: {hdr}".format(hdr=header))

        # Check if type is valid
        try:
            type = CommandID(header.type)
        except ValueError:
            print("Server: Invalid packet type: {t}".format(t=type), file=sys.stderr)
            return False

        # How do we handle the type?
        if type == CommandID.MOTORSETTINGS:
            data = PacketMotorSettings._make(struct.unpack(PacketMotorSettings.FORMAT, data))
            self.on_motorsettings_received(data)
        elif type == CommandID.MOTORSPEED:
            data = PacketMotorSpeed._make(struct.unpack(PacketMotorSpeed.FORMAT, data))
            self.on_motorspeed_received(data)
        elif type == CommandID.MOTORSTOP:
            self.on_motorstop_received()
        else:
            print("Server: Command ID not implemented: {t}".format(t=type), file=sys.stderr)

        return True

    def on_motorspeed_received(self, data: PacketMotorSpeed):
        """
        Simply calls motor script to set speed
        """
        print("Setting motor speed: left={0}, right={1}".format(data.speed_left, data.speed_right))
        motor_control.move_tank(data.speed_left, data.speed_right)

    def on_motorstop_received(self):
        """
        Simply calls motor script to stop
        """
        print("Stopping motors")
        motor_control.stop_tank()

    def on_motorsettings_received(self, data: PacketMotorSettings):
        """
        Not yet implemented
        Should set various settings regarding motor for example
        """
        raise NotImplementedError(str(data))

if __name__ == '__main__':
    """
    Standalone test block
    """
    args = argparse.ArgumentParser()

    args.add_argument('-c', '--config', dest='config', action=FullPath, type=str, default=pathtools.fullpath('/etc/marvin42_tdrc'), help="Custom config file (optional)", metavar='filepath')
    args = args.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    server = Receiver((config['server']['bind_address'], int(config['server']['bind_port'])), int(config['server']['max_connections']))
    while True:
        try:
            server.poll()
        except KeyboardInterrupt:
            break
        
    sys.exit(0)
