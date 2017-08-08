from constants import MED_OK, MED_NO
from mcp import getclass
import random

conf = {}

def gc(name):
    return getclass(hostname, name)

def register(evname, **kwargs):
    def register_decorator(func):
        hooks = conf.setdefault(evname, [])
        hooks.append({'exec': func, 
                      'evtype': kwargs.get('evtype'),
                      'object': kwargs.get('object'),
                      'subject': kwargs.get('subject')})
        return func
    return register_decorator

@register('getprocess')
def getprocess(evtype, parent):
    print("//////////****")
    tmp = gc('fuck')
    print(tmp)
    print("****//////////")
    #print(evtype)
    #print(parent)
    return MED_OK

@register('getfile', evtype={'filename': '/'})
def getfile(evtype, new_file, parent):
    print('som root vyfiltrovany cez dictionary')
    print(evtype)
    return MED_OK

@register('getfile', evtype={'filename': lambda x: x == '/'})
def getfile(evtype, new_file, parent):
    print('som root vyfiltrovany cez lambdu v dictionary')
    print(evtype)
    return MED_OK

@register('getfile', evtype=lambda e: e['filename'] == '/')
def getfile(evtype, new_file, parent):
    print('som root vyfiltrovany cez lambdu')
    print(evtype)
    return MED_OK

@register('getfile')
def getfile2(evtype, new_file, parent):
    print(evtype)
    return MED_OK

@register('kill')
def kill(etype, subj, obj):
    return MED_NO

@register('fork')
def fork(evtype, subj):
    #if random.random() < 0.2:
    #    return MED_NO
    return MED_OK
