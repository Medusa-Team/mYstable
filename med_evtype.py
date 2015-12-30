import struct
from med_attr import Attr, AttrInit, readAttribute, MEDUSA_COMM_ATTRNAME_MAX
from helpers import complement

class Evtype(AttrInit):
        ''' 
        initializer reads from 'medusa' interface to initialize objects values
        TODO:   create object factory for this purpose, because we need empty initializer
                for 'UPDATE' medusa command
        '''
        def __init__(self, buf):
                AttrInit.__init__(self, buf)

# TODO TODO TODO: fix documentation in 'include/linux/medusa/l4/comm.h'
# error in 'actbit' documentation in 'include/linux/medusa/l4/comm.h'
''' medusa event definition in 'include/linux/medusa/l4/comm.h'
    struct medusa_comm_evtype_s {
        u_int64_t evid;         // unique identifier of this event
        u_int16_t size;         // size of event in memory
        // which bit of 'act' controls this evtype:
        //      0xc000 + bitnr: bitnr at OBJECT
        //      0x0000 + bitnr: bitnr at SUBJECT
        //      0xffff: there is no way to trigger this event
        u_int16_t actbit;
        u_int64_t ev_kclass[2];
        char name[MEDUSA_COMM_EVNAME_MAX];
        char ev_name[2][MEDUSA_COMM_ATTRNAME_MAX];
'''
MEDUSA_COMM_EVNAME_MAX     = 32-2

# acc_type defined in 'include/linux/medusa/l3/kobject.h'
# evtypes
MEDUSA_EVTYPE_NOTTRIGGERED =            0xffff
MEDUSA_EVTYPE_TRIGGEREDATSUBJECT =      0x0000
MEDUSA_EVTYPE_TRIGGEREDATOBJECT =       0x8000
MEDUSA_EVTYPE_TRIGGEREDBYSUBJECTBIT =   0x0000
MEDUSA_EVTYPE_TRIGGEREDBYOBJECTBIT =    0x4000
# acctypes:
# not triggered - monitoring of this event can't be turned off
MEDUSA_ACCTYPE_NOTTRIGGERED = MEDUSA_EVTYPE_NOTTRIGGERED
# triggered by subject - the event is triggered by changing the subject
MEDUSA_ACCTYPE_TRIGGEREDATSUBJECT = \
        MEDUSA_EVTYPE_TRIGGEREDATSUBJECT | MEDUSA_EVTYPE_TRIGGEREDBYSUBJECTBIT
# triggered by object - the event is triggered by changing the object
MEDUSA_ACCTYPE_TRIGGEREDATOBJECT = \
        MEDUSA_EVTYPE_TRIGGEREDATOBJECT | MEDUSA_EVTYPE_TRIGGEREDBYOBJECTBIT

'''
evtypedef message format
        size |  type                    | content
        ----------------------------------------------------
          8  |  const                   | NULL
          4  |  const                   | ACCTYPEDEF
          ?  |  medusa_comm_acctype_s   | acctype definition
          ?  |  medusa_comm_attribute_s | attribute[]
'''
def readEvtypedef(medusa, ENDIAN = "="):
        medusa_comm_evtype_s = (ENDIAN+"QHHQQ"+str(MEDUSA_COMM_EVNAME_MAX)+"s"+\
                str(MEDUSA_COMM_ATTRNAME_MAX)+"s"+str(MEDUSA_COMM_ATTRNAME_MAX)+"s",
                8+2+2+8+8+MEDUSA_COMM_EVNAME_MAX+2*MEDUSA_COMM_ATTRNAME_MAX)

        def __init__(self, buf):
                Evtype.__init__(self, buf)

        evid, size, actbit, ev_kclass0, ev_kclass1, name, ev_name0, ev_name1 = \
                struct.unpack(medusa_comm_evtype_s[0], \
                medusa.read(medusa_comm_evtype_s[1]))
        name = name.decode('ascii')
        ev_name0 = ev_name0.decode('ascii')
        ev_name1 = ev_name1.decode('ascii')
        if ev_name0 == ev_name1:
                ev_kclass1 = None
                ev_name1 = None
        if actbit & MEDUSA_ACCTYPE_TRIGGEREDATOBJECT:
                actbitStr = 'object'
        else:
                actbitStr = 'subject'
        actbit &= complement(MEDUSA_ACCTYPE_TRIGGEREDATOBJECT)
        print("REGISTER evtype '%s' (%s, %s) with size=%d, id=%0x (%s, actbit = %s) {" % \
                (name, ev_name0, ev_name1, size, evid, actbitStr, hex(actbit)), end='')

        event = type(name,(Evtype,),dict(__init__=__init__))
        #events[evid] = {'name':name, 'size':size, 'ev0':ev0, 'ev1':ev1, 'attr': None}
        event.evid = evid
        event.size = size
        event.name = name
        event.performedOn = actbitStr
        event.actbit = actbit
        event.subType = ev_kclass0
        event.subName = ev_name0
        event.objType = ev_kclass1
        event.objName = ev_name1
        event.attr = dict()

        # read attributes
        attrMaxOffset = -1
        sizeReal = 0
        attrCnt = 0
        while True:
                attr = readAttribute(medusa, ENDIAN)
                if attr == None:
                        break;
                event.attr[attr.name] = attr
                attrCnt += 1
                if attr.offset > attrMaxOffset:
                        sizeReal = attr.offset + attr.length
                        attrMaxOffset = attr.offset
                print("\n\t%s '%s' (offset = %d, len = %d)" % \
                        (attr.typeStr, attr.name, attr.offset, attr.length), end='')
        if attrCnt:
                print('')
        print("}")

        # check for real size of object
        # because 'acctype_id' is accounted into event object structure
        # at offset 0, len 8 Bytes
        # if it is no attr, size should be 8
        if not sizeReal:
                sizeReal += 8
        if size != sizeReal:
                print("WARNING: real size of '%s' is %dB" % (name, sizeReal))
        print("")

        return event
