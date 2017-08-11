from constants import MED_OK, MED_NO
from framework import Register
import random

register = Register()

def printk(*args):
    s = Printk()
    for m in args:
        msg = str(m)
        for i in msg.split('\n'):
            s['message'] = i
            s.update()

#@register('init')
def init():
    tmp = Fuck()
    print(tmp)
    tmp['action'] = 'hocico'
    tmp['dev'] = 0x76543211
    tmp['ino'] = 0xdeadbaba
    tmp['path'] = '/home/jano/asd.txt'
    #tmp.fetch()
    #print(tmp)
    #tmp.attr['action'].val = 'append'
    #tmp.attr['path'].val = '/home/jano/asd2.txt'
    #tmp.update()

    for i in range(1, 7):
        printk("cislo %d zije" % i)

@register('getprocess')
def getprocess(evtype, parent):
    if parent['gid'] == 0:
        printk("getprocess: parent gid ROOT")
    else:
        printk("getprocess: change parent gid %d of '%s' to ROOT" % (parent['gid'], parent['cmdline']))
        parent['gid'] = 0
        parent.update()

    tmp = Process()
    print(tmp)

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
    printk("getfile('%s')" % evtype['filename'])
    print(new_file)
    f = File()
    return MED_OK

@register('kill')
def kill(etype, subj, obj):
    return MED_NO

@register('fork')
def fork(evtype, subj):
    #if random.random() < 0.2:
    #    return MED_NO
    return MED_OK
