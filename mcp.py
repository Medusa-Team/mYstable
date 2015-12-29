'''
Medusa Communication Protocol
'''

import struct

from comm import CommFile
from med_attr import Attr, readAttribute, MEDUSA_COMM_ATTRNAME_MAX
from med_kclass import Kclass, readKclassdef
from med_evtype import Evtype, readEvtypedef
from helpers import printHex

do_cmd = dict()         # list of pairs {cmd: do_cmd_fnc}
kclasses = dict()       # kclasses obtained from medusa
events = dict()         # events obtained from medusa

DEBUG = 1
ENDIAN = "="

# TODO: protokol zavisly od implementacie v jadre!!!
# see include/linux/medusa/l4/comm.h

# version of this communication protocol
MEDUSA_COMM_VERSION  = 1
MEDUSA_COMM_GREETING = 0x66007e5a

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

# answer codes
MED_ERR =       -1
MED_YES =       0
MED_NO =        1
MED_SKIP =      2
MED_OK =        3

# decorator
def registerCmd(cmd):
        def decorator(fnc):
                do_cmd[cmd] = fnc
                return fnc
        return decorator

'''
*********************************************************************
EXCEPTIONS
*********************************************************************
'''

# TODO: exceptions
class MedusaCommError(RuntimeError): pass

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
@registerCmd(MEDUSA_COMM_AUTHREQUEST)
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

        print("[0x%08X] %s: %s" % (request_id, acctype.name, acctype.subName), end='')
        if acctype.objName:
                print(", %s" % acctype.objName, end='')
        print()

        evid = struct.unpack(ENDIAN+"Q", medusa.read(8))[0]
        evtype = events.get(evid)
        # TODO: MedusaCommError -> MedusaWhatEver
        if evtype == None:
                raise(MedusaCommError("unknown EVENT type "+hex(evid)+"in ACCESS "+acctype.name))
        if evtype != acctype:
                print("WARNING: access type differs from event type")
        evbuf = b''
        if acctype.size-8 > 0:
                evbuf = (8*(None,)) + struct.unpack(ENDIAN+str(acctype.size-8)+"B", medusa.read(acctype.size-8))
        event = evtype(evbuf)
        if DEBUG:
                print("DEBUG: access event '" + evtype.name + "'", event)

        # read ev0 kclass - subject type
        subType = kclasses.get(acctype.subType)
        # TODO: MedusaCommError -> MedusaWhatEver
        if subType == None:
                raise(MedusaCommError("unknown subject KCLASS type for: '"+acctype.subName+"'"))
        sub = subType(struct.unpack(ENDIAN+str(subType.size)+"B", medusa.read(subType.size)))
        if DEBUG:
                print("DEBUG: subject '" + acctype.subName + "' of", sub)

        # read ev1 kclass - object type
        obj = None
        if acctype.objType:
                objType = kclasses.get(acctype.objType)
                # TODO: MedusaCommError -> MedusaWhatEver
                if objType == None:
                        raise(MedusaCommError("unknown object KCLASS type for: '"+acctype.objName+"'"))
                obj = objType(struct.unpack(ENDIAN+str(objType.size)+"B", medusa.read(objType.size)))
                if DEBUG:
                        print("DEBUG: object '" + acctype.objName + "' of", obj)

        if DEBUG:
                print('------- AUTHREQUEST END -------')

        # TODO TODO TODO decide...
        # decide(event, sub, obj)

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
@registerCmd(MEDUSA_COMM_AUTHANSWER)
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
@registerCmd(MEDUSA_COMM_KCLASSDEF)
def doMedusaCommKclassdef(medusa):
        global kclasses
        kclass = readKclassdef(medusa, ENDIAN)
        # TODO: raise 'kclass already defined'
        if kclass.kclassid in kclasses:
                raise MedusaCommError
        kclasses[kclass.kclassid] = kclass

#MEDUSA_COMM_KCLASSUNDEF    = 0x03 # k->c
@registerCmd(MEDUSA_COMM_KCLASSUNDEF)
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
@registerCmd(MEDUSA_COMM_EVTYPEDEF)
def doMedusaCommEvtypedef(medusa):
        global events
        event = readEvtypedef(medusa, ENDIAN)
        # TODO: raise 'event already defined'
        if event.evid in events:
                raise MedusaCommError
        events[event.evid] = event

#MEDUSA_COMM_EVTYPEUNDEF    = 0x05 # k->c
@registerCmd(MEDUSA_COMM_EVTYPEUNDEF)
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
@registerCmd(MEDUSA_COMM_FETCH_REQUEST)
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
@registerCmd(MEDUSA_COMM_FETCH_ANSWER)
def doMedusaCommFetchAnswer(medusa):
        print("TODO: doMedusaCommFetchAnswer")
        raise(NotImplementedError)

'''
fetch_error message format
'''
#MEDUSA_COMM_FETCH_ERROR    = 0x09 # k->c
@registerCmd(MEDUSA_COMM_FETCH_ERROR)
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
@registerCmd(MEDUSA_COMM_UPDATE_REQUEST)
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
@registerCmd(MEDUSA_COMM_UPDATE_ANSWER)
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

