import os
import platform
import socket
import dns.resolver

def getCommType():
#    print("getcommtype")
    return {"net": ("CommNet", checkNet, __name__)}

def checkNet(hosts, good, conflict, wrong):

    for host in hosts:
        remote_device = host['host_commdev']

        result = ping(remote_device)
        if result is False:
            wrong.append(host)
            continue

    check_net_IP_duplicities(hosts, good, conflict, wrong)


def check_net_IP_duplicities(hosts, good, conflict, wrong):

    resolver = dns.resolver.Resolver()
    resolver.timeout = 2 #2 seconds time out if no response to avoid long waiting

    dns_lookups = dict()
    for host in hosts:
        name = host['host_name']
        net_addres = host['host_commdev']

        # store dns lookups for each host separately
        try:
            answer = resolver.query(net_addres)
        except:
            pass  #TODO TODO TODO
            # wrong.append(host)
        else:
            addr_set = set(rdata.address for rdata in answer)
            dns_lookups[name] = addr_set

    host_names_to_del = []
    for name1,set1 in dns_lookups.values(): # je to dobreeee???? dvojity for na tom istom???
        for name2,set2 in dns_lookups.values():
            if bool( set1.intersection(set2)) is True: #if intersection is non empty set
                host_names_to_del.append(name1)
                host_names_to_del.append(name2)

    # here find hosts with name and append it to list conflict


def ping(host):
    """
    Returns True if host responds to a ping request
    """
    sys = platform.system().lower()
    if sys == 'linux':
        #sent only 1 packet and wait for response max 1 second
        ping_cmd = '-c 1 -W 1 ' + host + ' >> /dev/null'
    else:
        raise NotImplementedError

    # Ping
    return os.system('ping ' + ping_cmd) == 0