import sys, struct
from networking import PacketReceiver, PacketHeader

try:
    import motorctrl
except:
    pass

import marvin42_types
from marvin42_types import *

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
        motorctrl.move_Tank(data.speed_left, data.speed_right)

    def on_motorsettings_received(self, data: PacketMotorSettings):
        print(data)

if __name__ == '__main__':
    server = Receiver((marvin42_config.SERVER_ADDRESS, marvin42_config.SERVER_PORT), marvin42_config.SERVER_MAX_CONNECTIONS)
    while True:
        try:
            server.poll()
        except KeyboardInterrupt:
            break

sys.exit(0)
