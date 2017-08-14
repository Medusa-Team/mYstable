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
from queue import Queue
from threading import Thread, Lock, Event
from constants import MED_OK, MED_NO
from framework import exec
from mcp import doMedusaCommAuthanswer


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

    return comms


class Comm(object):

    def __init__(self, host):
        self.host_name = host['host_name']
        self.host_confdir = host['host_confdir']
        self.host_commtype = host['host_commtype']
        self.host_commdev = host['host_commdev']
        self.hook_module = host['hook_module']
        self.hook_list = self.hook_module.register.hooks
        if self.hook_list is None:
            self.hook_list = {}
        # thread for auth requests handling
        self.requestsQueue = Queue()
        # requests (fetch/update) from auth server to medusa
        self.requestsAuth2Med = dict()
        self.requestsAuth2Med_lock = Lock()
        # event if 'init' from user module is done
        self.init_executed = Event()
        self.init_executed.clear()
        self.init_done = False
        self.requestsThread = Thread(name="requestThread",target=Comm.decideQueue, args=(self,))
        self.requestsThread.start()

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, *args):
        raise NotImplementedError

    def read(self, size):
        raise NotImplementedError

    def write(self, what):
        raise NotImplementedError

    def decideQueue(self):
        self.init_executed.wait()
        while True:
            request_id, evtype, subj, obj = self.requestsQueue.get()
            res = self.decide(evtype, subj, obj)
            print("Comm.decideQueue: evtype='%s', request_id=%x, res=%x" % (evtype._name, request_id, res))
            doMedusaCommAuthanswer(self, request_id, res)
            self.requestsQueue.task_done()

    def decide(self, event, subj, obj):
        def _doCheck(check, kobject):
            if check is None:
                return True
            return exec(check, kobject)

        for hook in self.hook_list.get(event._name, []):
            try:
                if not _doCheck(hook['event'], event): continue
                if not _doCheck(hook['object'], obj): continue
                if not _doCheck(hook['subject'], subj): continue
                if obj is None:
                    res = hook['exec'](event, subj)
                else:
                    res = hook['exec'](event, subj, obj)
                if res == MED_NO:
                    return res
            except Exception as err:
                import traceback, sys
                traceback.print_exc(file=sys.stdout)
                for arg in err.args:
                    print("error in hook: %s" % arg)
                pass #todo error msg

        return MED_OK

    def init(self):
        for hook in self.hook_list.get('init', []):
            try:
                hook['exec']()
            except Exception as e:
                print(e)
        self.init_executed.set()

    def __str__(self):
        return '%s = {\n        host_name = %s\n        host_confdir = %s\n        host_commtype = %s\n        host_commdev = %s\n}' % (type(self), self.host_name, self.host_confdir, self.host_commtype, self.host_commdev)

