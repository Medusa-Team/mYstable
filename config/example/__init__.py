from constants import MED_OK, MED_NO
from framework import Register, NameSpace
from bitmap import Bitmap
import random
import os

ns = NameSpace()
register = Register()

def printk(*args):
    s = Printk()
    for m in args:
        msg = str(m)
        for i in msg.split('\n'):
            s.message = i
            s.update()

@register('init')
def init():

    #process1 = Process()
    process2 = Process()

    #process1.pid = 4783
    #process1.fetch()
    #process2.pid = 4783
    #process2.fetch()

    #process1.ecap[0] = True

    #print('init process2.ecap before -----------------')
    #print(process2.ecap)

    #raise BaseException



    #bm = Bitmap(bytes(16)).tobytes() # 00000000 00000000
    #bm[0] = True
    #process.ecap[0] = True
    #process.update()
    #process.fetch()
    #print('init process.ecap after -----------------')
    #print(process.ecap)
    #print(super(Bitmap, process.ecap).__str__())



    """
    tmp = Fuck()
    printk(tmp)
    tmp.action = 'hocico'
    tmp.path = '/home/jano/asd.txt'


    tmp.fetch()


    print(tmp)
    tmp.attr['action'].val = 'append'
    tmp.attr['path'].val = '/home/jano/asd2.txt'
    tmp.update()

    #for i in range(1, 7):
     #   printk("cislo %d zije" % i)
    """

@register('getprocess')
def getprocess(event, parent):

    printk('getprocess start')

    if parent.gid == 0:
        printk("getprocess: parent gid ROOT")
    else:
        printk("getprocess: change parent gid %d of '%s' to ROOT" % (parent.gid, parent.cmdline))
        parent.gid = 0
    parent.med_oact = Bitmap(16)
    parent.med_oact.set()
    parent.med_sact = Bitmap(16)
    parent.med_sact.set()

    parent.update()
    print(parent)

    tmp = Process()
    print(tmp)

    #print(event)
    #print(parent)
    return MED_OK

@register('getfile', event={'filename': '/'})
def getfile(event, new_file, parent):
    #print('som root vyfiltrovany cez dictionary')
    #print(event)
    return MED_OK

@register('getfile', event={'filename': lambda x: x == '/'})
def getfile(event, new_file, parent):
    #print('som root vyfiltrovany cez lambdu v dictionary')
    #print(event)
    return MED_OK

@register('getfile', event=lambda e: e.filename == '/')
def getfile(event, new_file, parent):
    #print('som root vyfiltrovany cez lambdu')
    #print(event)
    return MED_OK

@register('getfile')
def getfile(event, new_file, parent):
    #print(event)
    printk("getfile('%s')" % event.filename)
    new_file.med_oact = Bitmap(b'\xff\xff')
    new_file.update()
    print(event.filename)
    print(new_file)
    return MED_OK

@register('kill')
def kill(event, subj, obj):
    return MED_NO

@register('fork')
def fork(event, subj):
    #if random.random() < 0.2:
    #    return MED_NO
    return MED_OK
