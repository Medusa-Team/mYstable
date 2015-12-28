'''
This module provide communication interface with the Medusa in kernel.
There are at least two possibilities to communicate:
        1. through '/dev/medusa' virtual character device
        2. network
For now, there is implemented only the first possibility,
by the class CommFile.
'''

import os

class Comm:
        def __init__(self):
                raise NotImplementedError
        def __enter__(self):
                raise NotImplementedError
        def __exit__(self, *args):
                raise NotImplementedError
        def read(self, size):
                raise NotImplementedError
        def write(self, what):
                raise NotImplementedError

class CommFile(Comm):
        def __init__(self, medFile='/dev/medusa'):
                self.fd = None
                self.fname = medFile
        def __enter__(self):
                self.fd = os.open(self.fname, os.O_RDWR)
                return self
        def __exit__(self, *args):
                os.close(self.fd)
        def read(self, size):
                return os.read(self.fd, size)
        def write(self, what):
                return os.write(self.fd, what)
