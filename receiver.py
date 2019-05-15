import sys, argparse, configparser, struct
from modules.pathtools import *
from modules.networking import PacketReceiver, PacketHeader
from modules.marvin42 import *

try:
    import motor_control
except (SystemError, ImportError):
    pass

class Receiver(PacketReceiver):
    def on_client_connected(self, host: tuple):
        print("Server: Client connected: {h}".format(h=host))

    def on_client_disconnected(self, host: tuple):
        print("Server: Client disconnected: {h}".format(h=host))

    def on_data_received(self, header: PacketHeader, data: bytes) -> bool:
        print("Server: Data received: {hdr}".format(hdr=header))

        try:
            type = CommandID(header.type)
        except ValueError:
            print("Server: Invalid packet type: {t}".format(t=type), file=sys.stderr)
            return False

        if type == CommandID.MOTORSPEED:
            data = PacketMotorSpeed._make(struct.unpack(PacketMotorSpeed.FORMAT, data))
            self.on_motorspeed_received(data)
        elif type == CommandID.MOTORSETTINGS:
            data = PacketMotorSettings._make(struct.unpack(PacketMotorSettings.FORMAT, data))
            self.on_motorsettings_received(data)
        else:
            print("Server: Command ID not implemented: {t}".format(t=type), file=sys.stderr)

        return True

    def on_motorspeed_received(self, data: PacketMotorSpeed):
        print(data)
        motor_control.move_Tank(data.speed_left, data.speed_right)

    def on_motorsettings_received(self, data: PacketMotorSettings):
        print(data)

if __name__ == '__main__':
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
