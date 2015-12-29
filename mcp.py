'''
Medusa Communication Protocol
'''

import struct

from comm import CommFile
from med_attr import Attr, readAttribute, MEDUSA_COMM_ATTRNAME_MAX
from med_kclass import Kclass

DEBUG = 1
ENDIAN = "="

# TODO: protokol zavisly od implementacie v jadre!!!
# see include/linux/medusa/l4/comm.h

# version of this communication protocol
MEDUSA_COMM_VERSION  = 1
MEDUSA_COMM_GREETING = 0x66007e5a

MEDUSA_COMM_KCLASSNAME_MAX = 32-2
MEDUSA_COMM_EVNAME_MAX     = 32-2

# comm protocol commands; 'k' stands for kernel, 'c' for constable

MEDUSA_COMM_AUTHREQUEST    = 0x01 # k->c
MEDUSA_COMM_AUTHANSWER     = 0x81 # c->k

MEDUSA_COMM_KCLASSDEF      = 0x02 # k->c
MEDUSA_COMM_KCLASSUNDEF    = 0x03 # k->c
MEDUSA_COMM_EVTYPEDEF      = 0x04 # k->c
MEDUSA_COMM_EVTYPEUNDEF    = 0x05 # k->c

MEDUSA_COMM_FETCH_REQUEST  = 0x88 # c->k
MEDUSA_COMM_FETCH_ANSWER   = 0x08 # k->c
MEDUSA_COMM_FETCH_ERROR    = 0x09 # k->c

MEDUSA_COMM_UPDATE_REQUEST = 0x8a # c->k
MEDUSA_COMM_UPDATE_ANSWER  = 0x0a # k->c

''' medusa class definition in 'include/linux/medusa/l4/comm.h'
    struct medusa_comm_kclass_s {
        u_int64_t kclassid;     // unique identifier of this kclass
        u_int16_t size;         // memory size consumed by object itself
        char name[MEDUSA_COMM_KCLASSNAME_MAX];  // string: class name
    }
'''
medusa_comm_kclass_s = (ENDIAN+"QH"+str(MEDUSA_COMM_KCLASSNAME_MAX)+"s", 8+2+MEDUSA_COMM_KCLASSNAME_MAX)

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
medusa_comm_evtype_s = (ENDIAN+"QHHQQ"+str(MEDUSA_COMM_EVNAME_MAX)+"s"+\
        str(MEDUSA_COMM_ATTRNAME_MAX)+"s"+str(MEDUSA_COMM_ATTRNAME_MAX)+"s",
        8+2+2+8+8+MEDUSA_COMM_EVNAME_MAX+2*MEDUSA_COMM_ATTRNAME_MAX)

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

# answer codes
MED_ERR =       -1
MED_YES =       0
MED_NO =        1
MED_SKIP =      2
MED_OK =        3

do_cmd = dict()         # list of pairs {cmd: do_cmd_fnc}
kclasses = dict()       # kclasses obtained from medusa
events = dict()         # events obtained from medusa

'''
*********************************************************************
EXCEPTIONS
*********************************************************************
'''

# TODO: exceptions
class MedusaCommError(RuntimeError): pass

'''
*********************************************************************
HELPER METHODS
*********************************************************************
'''

def complement(c, width=64):
        return c ^ (2**width-1)

def printHex(head, body):
        print(head, end='')
        for i in body:
                print("{:02x}".format(i), end='')
        print()

def registedCmd(cmd):
        def decorator(fnc):
                do_cmd[cmd] = fnc
                return fnc
        return decorator

'''
*********************************************************************
COMMUNICATION
*********************************************************************
'''

# TODO TODO TODO: request_id size differs in authanswer message format!!!
'''
authrequest message format:
        size |  type    | content
        ----------------------------
          8  |  const   | acctype_id
          4  |  const   | request_id, is always 0
         var |  access  | access object
         var |  kobject | target[]

'''
#MEDUSA_COMM_AUTHREQUEST    = 0x01 # k->c
# TODO requests -> locking
requests = []
@registedCmd(MEDUSA_COMM_AUTHREQUEST)
def doMedusaCommAuthrequest(medusa, acctype_id = None):
        if DEBUG:
                print('------- AUTHREQUEST BEG -------')
        # remember that acctype_id is just readed
        request_id = struct.unpack(ENDIAN+"I", medusa.read(4))[0]
        #print("DEBUG: request_id:", '{:08x}'.format(request_id))
        acctype = events.get(acctype_id)
        # TODO: MedusaCommError -> MedusaWhatEver
        if acctype == None:
                raise(MedusaCommError("unknown ACCESS type"))
        requests.append(request_id)

        print("[0x%08X] %s: %s" % (request_id, acctype['name'], acctype['ev0']['name']), end='')
        if acctype['ev1']:
                print(", %s" % acctype['ev1']['name'], end='')
        print()

        # read access
        acc = struct.unpack(ENDIAN+str(acctype['size'])+"B", medusa.read(acctype['size']))
        if DEBUG:
                printHex("DEBUG: acc: ", acc)

        # read ev0 kclass
        ev0_type = kclasses.get(acctype['ev0']['type'])
        # TODO: MedusaCommError -> MedusaWhatEver
        if ev0_type == None:
                raise(MedusaCommError("unknown KCLASS 0 type"))
        ev0 = ev0_type(struct.unpack(ENDIAN+str(ev0_type.size)+"B", medusa.read(ev0_type.size)))
        if DEBUG:
                print("DEBUG: subject '" + acctype['ev0']['name'] + "' of", ev0)

        # read ev1 kclass
        ev1 = None
        if acctype['ev1']:
                ev1_type = kclasses.get(acctype['ev1']['type'])
                # TODO: MedusaCommError -> MedusaWhatEver
                if ev1_type == None:
                        raise(MedusaCommError("unknown KCLASS 1 type"))
                ev1 = ev1_type(struct.unpack(ENDIAN+str(ev1_type.size)+"B", medusa.read(ev1_type.size)))
                if DEBUG:
                        print("DEBUG: object '" + acctype['ev1']['name'] + "' of", ev1)

        if DEBUG:
                print('------- AUTHREQUEST END -------')
        # TODO TODO TODO decide...
        doMedusaCommAuthanswer(medusa, requests.pop())

'''
authanswer message format:
        size |  type    | content
        --------------------------------
          8  |  const   | REQUEST_ANSWER
          8  |  const   | request_id, for now ignored by kernel
          2  |  const   | result_code
'''
#MEDUSA_COMM_AUTHANSWER     = 0x81 # c->k
@registedCmd(MEDUSA_COMM_AUTHANSWER)
def doMedusaCommAuthanswer(medusa, request_id = None, result = MED_NO):
        cmd = MEDUSA_COMM_AUTHANSWER
        # TODO raise
        if request_id == None:
                raise(MedusaCommError)
        answer = struct.pack(ENDIAN+"QQH", cmd, request_id, result)
        if DEBUG:
                printHex("DEBUG: answer: ", answer)
                print()
        medusa.write(answer)

'''
kclassdef message format
        size |  type                    | content
        ---------------------------------------------------
          8  |  const                   | NULL
          4  |  const                   | CLASSDEF
          ?  |  medusa_comm_kclass_s    | kclass definition
          ?  |  medusa_comm_attribute_s | attribute[]
'''
#MEDUSA_COMM_KCLASSDEF      = 0x02 # k->c
@registedCmd(MEDUSA_COMM_KCLASSDEF)
def doMedusaCommKclassdef(medusa):
        def __init__(self, buf):
                Kclass.__init__(self, buf)

        kclassid, csize, cname = \
                struct.unpack(medusa_comm_kclass_s[0], \
                medusa.read(medusa_comm_kclass_s[1]))
        # TODO: raise 'kclass already defined'
        if kclassid in kclasses:
                raise MedusaCommError
        cname = cname.decode('ascii')
        print("REGISTER class '%s' with id %0x (size = %d) {" % (cname, kclassid, csize), end='')
        #kclasses[kclassid] = {'size':csize, 'name':cname, 'attr':None}
        kclass = type(cname,(Kclass,),dict(__init__ = __init__))
        kclass.size = csize
        kclass.name = cname
        kclass.attr = dict()
        kclasses[kclassid] = kclass

        # read attributes
        attrMaxOffset = -1
        csizeReal = 0
        attrCnt = 0
        while True:
                attr = readAttribute(medusa, ENDIAN)
                if attr == None:
                        break;
                kclass.attr[attr.name] = attr
                attrCnt += 1
                if attr.offset > attrMaxOffset:
                        csizeReal = attr.offset + attr.length
                        attrMaxOffset = attr.offset
                print("\n\t%s '%s' (offset = %d, len = %d)" % \
                        (attr.typeStr, attr.name, attr.offset, attr.length), end='')
        if attrCnt:
                print("")
        print("}")
        # check for real size of object
        if csize != csizeReal:
                print("WARNING: real size of '%s' is %dB" % (cname, csizeReal))
                #kclasses[kclassid]['size'] = csizeReal
        print("")

#MEDUSA_COMM_KCLASSUNDEF    = 0x03 # k->c
@registedCmd(MEDUSA_COMM_KCLASSUNDEF)
def doMedusaCommKclassundef(medusa):
        print("TODO: doMedusaCommKclassundef")
        raise(NotImplementedError)

'''
evtypedef message format
        size |  type                    | content
        ----------------------------------------------------
          8  |  const                   | NULL
          4  |  const                   | ACCTYPEDEF
          ?  |  medusa_comm_acctype_s   | acctype definition
          ?  |  medusa_comm_attribute_s | attribute[]
'''
#MEDUSA_COMM_EVTYPEDEF      = 0x04 # k->c
@registedCmd(MEDUSA_COMM_EVTYPEDEF)
def doMedusaCommEvtypedef(medusa):
        global events
        evid, size, actbit, ev_kclass0, ev_kclass1, name, ev_name0, ev_name1 = \
                struct.unpack(medusa_comm_evtype_s[0], \
                medusa.read(medusa_comm_evtype_s[1]))
        name = name.decode('ascii')
        ev_name0 = ev_name0.decode('ascii')
        ev_name1 = ev_name1.decode('ascii')
        if actbit & MEDUSA_ACCTYPE_TRIGGEREDATOBJECT:
                actbitStr = 'object'
        else:
                actbitStr = 'subject'
        actbit &= complement(MEDUSA_ACCTYPE_TRIGGEREDATOBJECT)
        print("REGISTER evtype '%s' (%s, %s) with size=%d, id=%0x (%s, actbit = %s) {" % \
                (name, ev_name0, ev_name1, size, evid, actbitStr, hex(actbit)), end='')
        ev0 = { 'type':ev_kclass0, 'name':ev_name0 }
        if ev_name0 == ev_name1:
                ev1 = None
        else:
                ev1 = { 'type':ev_kclass1, 'name':ev_name1 }
        events[evid] = {'name':name, 'size':size, 'ev0':ev0, 'ev1':ev1, 'attr': None}

        # read attributes
        attrMaxOffset = -1
        sizeReal = 0
        attrCnt = 0
        while True:
                attr = readAttribute(medusa, ENDIAN)
                if attr == None:
                        break;
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
                #events[evid]['size'] = sizeReal
        print("")

        # TODO: append attributes to 'events'

#MEDUSA_COMM_EVTYPEUNDEF    = 0x05 # k->c
@registedCmd(MEDUSA_COMM_EVTYPEUNDEF)
def doMedusaCommEvtypeundef(medusa):
        print("TODO: doMedusaCommEvtypeundef")
        raise(NotImplementedError)

'''
fetch_request message format
        size  |  type    | content
        ---------------------------------
          8   |  const   | FETCH
          8   |  const   | object_classid
          8   |  const   | fetch_id
         var  |  kobject | object data
'''
#MEDUSA_COMM_FETCH_REQUEST  = 0x88 # c->k
@registedCmd(MEDUSA_COMM_FETCH_REQUEST)
def doMedusaCommFetchRequest(medusa):
        print("TODO: doMedusaCommFetchRequest")
        raise(NotImplementedError)

'''
fetch_answer message format
        size |  type    | content
        --------------------------------
          8  |  const   | NULL
          4  |  const   | FETCH_ANSWER
          8  |  const   | object_classid
          8  |  const   | fetch_id
         var |  kobject | object data
'''
#MEDUSA_COMM_FETCH_ANSWER   = 0x08 # k->c
@registedCmd(MEDUSA_COMM_FETCH_ANSWER)
def doMedusaCommFetchAnswer(medusa):
        print("TODO: doMedusaCommFetchAnswer")
        raise(NotImplementedError)

'''
fetch_error message format
'''
#MEDUSA_COMM_FETCH_ERROR    = 0x09 # k->c
@registedCmd(MEDUSA_COMM_FETCH_ERROR)
def doMedusaCommFetchError(medusa):
        print("TODO: doMedusaCommFetchError")
        raise(NotImplementedError)

'''
update_request message format
        size |  type    | content
        --------------------------------
          8  |  const   | UPDATE
          8  |  const   | object_classid
          8  |  const   | update_id
         var |  kobject | object data
'''
#MEDUSA_COMM_UPDATE_REQUEST = 0x8a # c->k
@registedCmd(MEDUSA_COMM_UPDATE_REQUEST)
def doMedusaCommUpdateRequest(medusa):
        print("TODO: doMedusaCommUpdateRequest")
        raise(NotImplementedError)

'''
update_answer message format
        size |  type | content
        ------------------------------
          8  |  const | NULL
          4  |  const | UPDATE_ANSWER
          8  |  const | object_classid
          8  |  const | update_id
          4  |  const | answer
'''
#MEDUSA_COMM_UPDATE_ANSWER  = 0x0a # k->c
@registedCmd(MEDUSA_COMM_UPDATE_ANSWER)
def doMedusaCommUpdateAnswer(medusa):
        print("TODO: doMedusaCommUpdateAnswer")
        raise(NotImplementedError)

#UNKNOWN CMD
def doMedusaCommUnknown(medusa):
        raise( MedusaCommError() )

'''
**************************************************************
'''

def doCommunicate():
        global ENDIAN
        with CommFile('/dev/medusa') as medusa:
                # read greeting and set byte order
                greeting = medusa.read(8)
                end_lit = b"\x5a\x7e\x00\x66\x00\x00\x00\x00"
                end_big = b"\x00\x00\x00\x00\x66\x00\x7e\x5a"
                if greeting == end_big:
                        ENDIAN = ">"
                        print("from medusa detected BIG ENDIAN byte order\n")
                elif greeting == end_lit:
                        ENDIAN = "<"
                        print("from medusa detected LITTLE ENDIAN byte order\n")
                else:
                        print("from medusa detected UNSUPPORTED byte order")
                        return(-1)

                while True:
                        # read next chunk of data to do
                        id = struct.unpack(ENDIAN+"Q",medusa.read(8))[0]

                        # if 'id' == 0, do (un)def kevents/kclasses...
                        if id == 0:
                                cmd = medusa.read(4)
                                cmd = struct.unpack(ENDIAN+"I",cmd)[0]
                                do_cmd.get(cmd, doMedusaCommUnknown)(medusa)
                        else:
                                doMedusaCommAuthrequest(medusa, id)

