import os
import platform
from comm import Comm


# TODO spravit z toho staticku metodu classy CommNet
def getCommType():
    return {"net": (CommNet, checkNet, __name__)}


# TODO spravit z toho staticku metodu classy CommNet
def checkNet(hosts):
    for host in hosts:
        res = ping(host)
        if res is False:
            # tu co zhodme cely konfig? alebo len vypisat ze unable to ping host...
            raise ConnectionError('Unable ping host ' + host)


# TODO spravit z toho staticku metodu classy CommNet
def ping(host):
    """
    Returns True if host responds to a ping request
    """
    sys = platform.system().lower()
    if sys == 'linux':
        ping_cmd = '-c 1 ' + host + ' >> /dev/null'
    else:
        ping_cmd = '-n 1 ' + host + ' > NUL'

    # Ping with only one packet
    return os.system('ping ' + ping_cmd) == 0


class CommNet(Comm):
    def __init__(self, host):
        super().__init__(host)
        # raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, *args):
        raise NotImplementedError

    def read(self, size):
        raise NotImplementedError

    def write(self, what):
        raise NotImplementedError
