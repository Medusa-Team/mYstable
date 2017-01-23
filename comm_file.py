import os
from comm import Comm

#TODO spravit z toho staticku metodu classy CommNet
def getCommType():
    return {"file": (CommFile, checkFile, __name__)}

#TODO spravit z toho staticku metodu classy CommNet
def checkFile(files):
    for file in files:
        writeable = os.access(file, os.W_OK)  # check if it is possible to write into file
        if writeable is False:
            raise AttributeError("It is not possible to write into file '" + file + "'")


class CommFile(Comm):
    def __init__(self, host):
        super().__init__(host)
        self.fd = None
        #self.fname = medFile

    def __enter__(self):
        self.fd = os.open(self.host_commdev, os.O_RDWR)
        return self

    def __exit__(self, *args):
        os.close(self.fd)

    def read(self, size):
        return os.read(self.fd, size)

    def write(self, what):
        return os.write(self.fd, what)