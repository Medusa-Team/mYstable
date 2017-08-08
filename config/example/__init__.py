from constants import MED_OK, MED_NO
from mcp import getclass
import random

conf = {}

def gc(name):
    return getclass(hostname, name)

def register(evname):
    def register_decorator(func):
        hooks = conf.setdefault(evname, [])
        hooks.append({'exec': func})
        return func
    return register_decorator

@register('getprocess')
def getprocess(evtype, parent, none):
    print("//////////****")
    tmp = gc('fuck')
    print(tmp)
    print("****//////////")
    #print(evtype)
    #print(parent)
    return MED_OK

@register('getfile')
def getfile(evtype, new_file, parent):
    print(evtype)
    print(new_file)
    print(parent)
    return MED_OK

@register('kill')
def kill(etype, subj, obj):
    return MED_NO

@register('fork')
def fork(evtype, subj, obj):
    #if random.random() < 0.2:
    #    return MED_NO
    return MED_YES
