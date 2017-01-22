import os, platform

def getCommType():
#    print("getcommtype")
    return {"net": ("CommNet", checkNet, __name__)}

def checkNet(hosts):

    for host in hosts:
        res = ping(host)
        if res is False:
            # tu co zhodme cely konfig? alebo len vypisat ze unable to ping host...
            raise ConnectionError('Unable ping host ' + host)


def ping(host):
    """
    Returns True if host responds to a ping request
    """
    sys = platform.system().lower()
    if sys == 'linux':
        ping_cmd = '-c 1 ' + host + ' >> /dev/null'
    else:
        ping_cmd = '-n 1 ' + host + ' > NUL'

    # Ping
    return os.system('ping ' + ping_cmd) == 0