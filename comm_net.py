import os, platform
import socket

def getCommType():
#    print("getcommtype")
    return {"net": ("CommNet", checkNet, __name__)}

def checkNet(hosts):

    for host in hosts:
        res = ping(host)
        if res is False:
            # tu co zhodme cely konfig? alebo len vypisat ze unable to ping host...
            raise ConnectionError('Unable ping host ' + host)


def check_net_IP_duplicities(hosts):
    net_devices = [host['host_commdev'] for host in hosts if host['host_commtype'] == 'net']
    unique_net_devs = set()

    for net_dev in net_devices:
        try:
            dns = socket.getaddrinfo(net_dev, None)
        except socket.gaierror:
            raise ConnectionError('Cannot perform DNS lookup for host ' + net_dev)
        else:
            unique_net_devs.add(dns[0][4][0])  # add IP address of actual net device

    if len(net_devices) != len(unique_net_devs):
        raise AttributeError("Each host of type 'net' must have unique network device")


def ping(host):
    """
    Returns True if host responds to a ping request
    """
    sys = platform.system().lower()
    if sys == 'linux':
        ping_cmd = '-c 1 ' + host + ' >> /dev/null'
    else:
        raise NotImplementedError

    # Ping
    return os.system('ping ' + ping_cmd) == 0