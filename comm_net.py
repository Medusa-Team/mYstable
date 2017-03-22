import os
import platform
from comm import Comm
import dns.resolver
import subprocess


# TODO spravit z toho staticku metodu classy CommNet
def getCommType():
    return {"net": (CommNet, checkNet, __name__)}

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


def checkNet(hosts, good, conflict, wrong):

    loc_hosts = hosts[:] # make a copy

    for host in loc_hosts:
        remote_device = host['host_commdev']

        result = ping(remote_device)
        if result is False:
            wrong.append(host)
            loc_hosts.remove(host) # do not take hosts we cannot ping

    check_net_IP_duplicities(loc_hosts, good, conflict, wrong)


def check_net_IP_duplicities(hosts, good, conflict, wrong):

    resolver = dns.resolver.Resolver()
    resolver.timeout = 1 #1 seconds time out if no response to avoid long waiting

    ip_for_hosts = dict() # mapping IP addres -> host

    for host in hosts:
        name = host['host_name']
        net_addres = host['host_commdev']

        # store dns lookups for each host separately
        try:
            answer = resolver.query(net_addres)
        except Exception as err:
            wrong.append(host)
        else:
            addr_set = set(rdata.address for rdata in answer)
            for addres in addr_set: #store mapping IP -> list of hosts
                ip_for_hosts.setdefault(addres, []).append(host)


    # here add conflict hosts into conflicts
    for host_list in ip_for_hosts.values():
        if len(host_list) > 1:
            conflict.extend(host_list)
        else:
            good.extend(host_list)

# TODO spravit z toho staticku metodu classy CommNet
def ping(host):
    """
    Returns True if host responds to a ping request
    """
    sys = platform.system().lower()
    if sys != 'linux':
        raise NotImplementedError

    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        # call ping with 1 packet, waiting 1 second if no response, with no output at all
        subprocess.run(['ping', '-c 1', '-W 1', host], stdout=devnull, stderr=devnull, check=True)
    except subprocess.CalledProcessError:
        return False
    else:
        return True

