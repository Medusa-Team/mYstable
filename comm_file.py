import os
from comm import Comm
import subprocess

def getCommType():
    return {"file": (CommFile, checkFiles, __name__)}

class CommFile(Comm):
    def __init__(self, host):
        super().__init__(host)
        self.fd = None

    def __enter__(self):
        self.fd = os.open(self.host_commdev, os.O_RDWR)
        return self

    def __exit__(self, *args):
        os.close(self.fd)

    def read(self, size):
        return os.read(self.fd, size)

    def write(self, what):
        return os.write(self.fd, what)


def checkFiles(hosts, good, conflict, wrong):

    # good - no conflicts, file reachable
    # conflict - files reachable, but files points to equal inode eg. hard links / sym links
    # wrong - not reachable files at all

    inodes = dict() #mapping inode -> host(s)

    for host in hosts:
        # check if path is path to file,
        file = host['host_commdev']

        if os.path.isfile(file) is False:
            wrong.append(host)
            continue

        writeable = os.access(file, os.W_OK)  # check if it is possible to write into file
        if writeable is False:
            wrong.append(host)
            continue

        # result of command is '<device_number_decimal>:<inode_number>'
        stat_cmd = 'stat -Lc "%d:%i" ' + file
        stat_info = subprocess.check_output(stat_cmd, shell=True)
        stat_info = stat_info.decode()

        inodes.setdefault(stat_info, []).append(host)

    for inode_hosts in inodes.values():
        # couple hosts are sharing one inode - conflict
        if len(inode_hosts) > 1:
            conflict.extend(inode_hosts)
        else:
            # inode is owned by unique file and is accessible for writing
            good.append(inode_hosts)

