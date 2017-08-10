import os
from threading import Thread
from queue import Queue
from comm import Comm
import subprocess

def getCommType():
    return {"file": (CommFile, checkFiles, __name__)}

class CommFile(Comm):
    def initAttrs(self):
        self.readFd = None
        self.writeFd = None
        self.write_thread = None
        self.writeQueue = None

    def __init__(self, host):
        super().__init__(host)
        self.initAttrs()

    def __enter__(self):
        self.readFd = os.open(self.host_commdev, os.O_RDWR)
        self.writeFd = os.dup(self.readFd)
        self.writeQueue = Queue()
        self.writeThread = Thread(name="writeThread",target=CommFile.writeQueue, args=(self,))
        self.writeThread.start()
        return self

    def __exit__(self, *args):
        os.close(self.readFd)
        os.close(self.writeFd)
        self.initAttrs()

    def read(self, size):
        return os.read(self.readFd, size)

    def write(self, buf):
        self.writeQueue.put(buf)

    def writeQueue(self):
        while True:
            buf = self.writeQueue.get()
            try:
                os.write(self.writeFd , buf)
            except OSError as err:
                for arg in err.args:
                    print(arg)
            self.writeQueue.task_done()


def checkFiles(hosts, good, conflict, wrong):

    # good - no conflicts, file reachable
    # conflict - files reachable, but files points to equal inode eg. hard links / sym links
    # wrong - not reachable files at all

    inodes = dict() #mapping inode -> host(s)

    for host in hosts:
        # check if path is path to file,
        file = host['host_commdev']

        writeable = os.access(file, os.W_OK)  # check if it is possible to write into file
        if writeable is False:
            wrong.append(host)
            print('%s %s is not writeable' % (host, file))
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

