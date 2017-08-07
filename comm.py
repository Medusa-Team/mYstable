'''
This module provide communication interface with the Medusa in kernel.
There are at least two possibilities to communicate:
        1. through '/dev/medusa' virtual character device
        2. network
For now, there is implemented only the first possibility,
by the class CommFile.
'''

import os
from importlib import import_module
from constants import MED_OK, MED_NO


def getSupportedComms():

    comms = {}
    dirComms = '.'
    for dirName, subdirList, fileList in os.walk(dirComms):
        if dirName != dirComms:
            continue

        for fname in fileList:
            if not fname.startswith('comm'):
                continue
            if not fname.endswith('.py'):
                continue
            if fname[:-3] == __name__: #skip this module - comm.py
                continue

            try:
                fnameModule = import_module(fname[:-3], package=None)
            except ImportError as err:
                for arg in err.args:
                    print('module %s error: %s' % (fname, arg))
            else:
                comms.update(fnameModule.getCommType()) #add type of imported communication type
            print(comms)

    return comms


class Comm:

    def __init__(self, host):
        self.host_name = host['host_name']
        self.host_confdir = host['host_confdir']
        self.host_commtype = host['host_commtype']
        self.host_commdev = host['host_commdev']
        self.hook_list = host['hook_register']
        if self.hook_list is None:
            self.hook_list = {}

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, *args):
        raise NotImplementedError

    def read(self, size):
        raise NotImplementedError
        
    def write(self, what):
        raise NotImplementedError

    def decide(self, evtype, subj, obj):
        for hook in self.hook_list.get(evtype.name, []):
            try:
                res = hook['exec'](evtype, subj, obj)
                if res == MED_NO:
                    return res
            except:
                pass #todo error msg

        return MED_OK

    def __str__(self):
        return '{host_name: %s, host_confdir: %s, host_commtype: %s, host_commdev: %s}' % (self.host_name, self.host_confdir, self.host_commtype, self.host_commdev)

