import sys, os, argparse, configparser, struct, subprocess
from modules.pathtools import *
from modules.networking import PacketReceiver, PacketHeader
from modules.marvin42 import *

try:
    import motor_control
except (SystemError, ImportError):
    pass

class Receiver(PacketReceiver):
    __slots__ = ['cmd_proc', 'cmd_path']

    def __init__(self, host: tuple, max_connections: int = 10):
        super(Receiver, self).__init__(host, max_connections)
        self.cmd_proc = None
        self.cmd_path = "{p}/motor_control".format(p=os.path.dirname(os.path.realpath(__file__)))

    def run_command(self, op, *args):
        cmdlist = ["python3", "{p}/marvin42.py".format(p=self.cmd_path), op]
        cmdlist.extend(list(map(str, args)))

        print("Server: Attempt to execute command {cmd}".format(cmd=cmdlist))
        if self.cmd_proc is not None:
            if self.cmd_proc.poll() is None:
                self.cmd_proc.terminate()
                print("Server: Waiting for current command to terminate: {pid}".format(pid=self.cmd_proc.pid))
                self.cmd_proc.wait()

        self.cmd_proc = subprocess.Popen(cmdlist)
        (output_stdout, output_stderr) = self.cmd_proc.communicate()
        if self.cmd_proc.returncode is not None:
            if self.cmd_proc.returncode != 0:
                print("Server: Command failed: {cmd} ({pid})".format(cmd=cmdlist, pid=self.cmd_proc.pid))
                return False
            else:
                print("Server: Command succeded: {cmd} ({pid})".format(cmd=cmdlist, pid=self.cmd_proc.pid))
                return True
        else:
            print("Server: Command running: {cmd} ({pid})".format(cmd=cmdlist, pid=self.cmd_proc.pid))
            return True

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
        elif type == CommandID.MOTORSTOP:
            self.on_motorstop_received()
        elif type == CommandID.MOTORSETTINGS:
            data = PacketMotorSettings._make(struct.unpack(PacketMotorSettings.FORMAT, data))
            self.on_motorsettings_received(data)
        else:
            print("Server: Command ID not implemented: {t}".format(t=type), file=sys.stderr)

        return True

    def on_motorspeed_received(self, data: PacketMotorSpeed):
        print(data)
        self.run_command('run', data.speed_left, data.speed_right)
        #motor_control.move_Tank(data.speed_left, data.speed_right)

    def on_motorstop_received(self):
        self.run_command('stop')
        #motor_control.stop_tank()

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
