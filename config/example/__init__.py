from constants import MED_OK, MED_NO
from framework import Register
import random

register = Register()

@register('init')
def init():
    #tmp = Fuck()
    #tmp.attr['action'].val = 'hocico'
    #tmp.attr['dev'].val = 0x76543211
    #tmp.attr['ino'].val = 0xdeadbaba
    #tmp.attr['path'].val = '/home/jano/asd.txt'
    #tmp.fetch()
    #print(tmp)
    #tmp.attr['action'].val = 'append'
    #tmp.attr['path'].val = '/home/jano/asd2.txt'
    #tmp.update()
    s = Printk()
    s.attr['message'].val = "cislo 7 zije"
    s.update()
    s.update()
    s.update()

@register('getprocess')
def getprocess(evtype, parent):
    #print(evtype)
    #print(parent)
    return MED_OK

@register('getfile', evtype={'filename': '/'})
def getfile(evtype, new_file, parent):
    #print('som root vyfiltrovany cez dictionary')
    #print(evtype)
    return MED_OK

@register('getfile', evtype={'filename': lambda x: x == '/'})
def getfile(evtype, new_file, parent):
    #print('som root vyfiltrovany cez lambdu v dictionary')
    #print(evtype)
    return MED_OK

@register('getfile', evtype=lambda e: e['filename'] == '/')
def getfile(evtype, new_file, parent):
    #print('som root vyfiltrovany cez lambdu')
    #print(evtype)
    return MED_OK

@register('getfile')
def getfile2(evtype, new_file, parent):
    #print(evtype)
    return MED_OK

@register('kill')
def kill(etype, subj, obj):
    return MED_NO

@register('fork')
def fork(evtype, subj):
    #if random.random() < 0.2:
    #    return MED_NO
    return MED_OK
