import urllib3
from shadowsocks_handler.handler import ShadowsocksManager
ss = ShadowsocksManager('worker', '/tmp/shadowsocks-manager.sock')
