import socket
import time
import threading
import subprocess
import json

class ShadowsocksManager:
    cli = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    listening = False
    listener = None
    ssp = None
    config_data = None

    def __init__(self, shadowsocks, manager_address, config):
        self.ssserver = shadowsocks
        self.manager_address = manager_address
        self.socket_name = 'client'
        self.config = config
        self.config_data = json.loads(file(config, 'r').read())

    def get_socket_name(self):
        return '/tmp/ssclient-%s.sock' % self.socket_name

    def start_ss(self):
        self.ssp = subprocess.Popen([self.ssserver, '--manager-address', self.manager_address, '-c', self.config])
        time.sleep(5) # wait for ssstart
        self.cli.bind(self.get_socket_name())
        self.cli.connect(self.manager_address)

    def stop_ss(self):
        print 'exit'
        self.stop_listen()
        self.ssp.kill()
        subprocess.call(['rm', self.manager_address, self.get_socket_name()])

    def ping(self):
        return self._send_cmd('ping')

    def add(self, port, password):
        msg = 'add: {"server_port":%s, "password": "%s" }' % (port, password)
        self.config_data['port_password'][port] = password
        file(self.config, 'w').write(json.dumps(self.config_data))
        return self._send_cmd(msg)

    def remove(self, port):
        msg = 'add: {"server_port":%s}' % port
        del self.config_data['port_password'][port]
        file(self.config, 'w').write(json.dumps(self.config_data))
        return self._send_cmd(msg)

    def start_listen(self, callback):
        self.listening = True
        self.listener = threading.Thread(target=self._listen, args=(callback,))

    def stop_listen(self):
        if self.listening:
            self.listening = False
        while self.listener.isAlive():
            time.sleep(1)

    def _listen(self, callback):
        while self.listening:
            print self.listening
            callback(self.cli.recv(1506))

    def _close_socket(self):
        self.cli.shutdown()
        self.cli.close()

    def _send_cmd(self, msg):
        self.cli.send(msg.encode('utf-8'))
        return self.cli.recv(1506)

if __name__ == '__main__':
    def prt(data):
        print data
    ssserver = ShadowsocksManager('/tmp/shadowsocks-manager.sock')
    print ssserver.ping()
    ssserver.listen_async(prt)
    print 'sleep'
    time.sleep(3)
    ssserver.stop()
    exit()
