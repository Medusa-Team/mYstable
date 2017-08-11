'''
Medusa Communication Protocol
'''

import struct
import random
import threading

import med_endian
import med_kclass
from med_evtype import Evtype, readEvtypedef
from constants import *
from helpers import printHex

DEBUG = 1

do_cmd = dict()         # list of pairs {cmd: do_cmd_fnc}
hosts = dict()          # list of hosts contolled by this instance of auth server

# decorator
def registerCmd(cmd):
    def decorator(fnc):
        do_cmd[cmd] = fnc
        return fnc
    return decorator

def doMedusaRequest(host, obj, cmd, req_lock):
    if obj == None:
        raise(MedusaCommError)
    req_id = random.getrandbits(64)
    head = struct.pack(med_endian.ENDIAN+"QQQ", cmd, obj.kclassid, req_id)
    data = obj.pack()
    try:
        host.write(head + data)
    except OSError as err:
        print_err(err)

    host.requestsAuth2Med_lock.acquire()
    try:
        host.requestsAuth2Med[req_id] = obj
    except Exception as e:
        print(e)
    host.requestsAuth2Med_lock.release()
    req_lock.wait()

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
@registerCmd(MEDUSA_COMM_AUTHREQUEST)
def doMedusaCommAuthrequest(host, acctype_id = None):
    if DEBUG > 1:
        print('------- AUTHREQUEST BEG -------')
    # remember that acctype_id is just readed
    try:
        request_id = struct.unpack(med_endian.ENDIAN+"I", host.read(4))[0]
    except OSError as err:
        print_err(err)

    #print("DEBUG: request_id:", '{:08x}'.format(request_id))
    acctype = hosts[host.host_name]['events'].get(acctype_id)
    # TODO: MedusaCommError -> MedusaWhatEver
    if acctype == None:
        raise(MedusaCommError("unknown ACCESS type"))

    if DEBUG > 1:
        print("[0x%08X] %s: %s" % (request_id, acctype.name, acctype.subName), end='')
        if acctype.objName:
            print(", %s" % acctype.objName, end='')
        print()

    try:
        evid = struct.unpack(med_endian.ENDIAN+"Q", host.read(8))[0]
    except OSError as err:
        print_err(err)

    evtype = hosts[host.host_name]['events'].get(evid)
    # TODO: MedusaCommError -> MedusaWhatEver
    if evtype == None:
        raise(MedusaCommError("unknown EVENT type "+hex(evid)+"in ACCESS "+acctype.name))
    if evtype != acctype:
        print("WARNING: access type differs from event type")
    evbuf = b''
    if acctype.size-8 > 0:
        try:
            evbuf = (8*(None,)) + struct.unpack(med_endian.ENDIAN+str(acctype.size-8)+"B", host.read(acctype.size-8))
        except OSError as err:
            print_err(err)

    event = evtype(evbuf)
    if DEBUG > 1:
        print("DEBUG: access event '" + evtype.name + "'", event)

    # read ev0 kclass - subject type
    subType = hosts[host.host_name]['kclasses'].get(acctype.subType)
    # TODO: MedusaCommError -> MedusaWhatEver
    if subType == None:
        raise(MedusaCommError("unknown subject KCLASS type for: '"+acctype.subName+"'"))
    try:
        sub = subType(struct.unpack(med_endian.ENDIAN+str(subType.size)+"B", host.read(subType.size)))
    except OSError as err:
        print_err(err)

    if DEBUG > 1:
        print("DEBUG: subject '" + acctype.subName + "' of", sub)

    # read ev1 kclass - object type
    obj = None
    if acctype.objType:
        objType = hosts[host.host_name]['kclasses'].get(acctype.objType)
        # TODO: MedusaCommError -> MedusaWhatEver
        if objType == None:
            raise(MedusaCommError("unknown object KCLASS type for: '"+acctype.objName+"'"))
        try:
            obj = objType(struct.unpack(med_endian.ENDIAN+str(objType.size)+"B", host.read(objType.size)))
        except OSError as err:
            print_err(err)

        if DEBUG > 1:
            print("DEBUG: object '" + acctype.objName + "' of", obj)
    # INIT
    if not host.init_done:
        host.init_done = True
        threading.Thread(target=host.init).start()

    if DEBUG > 1:
        print('------- AUTHREQUEST END -------')

    #if DEBUG > 1:
    #    print(host)

    host.requestsQueue.put((request_id, event, sub, obj))

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
def doMedusaCommAuthanswer(host, request_id = None, result = MED_NO):
    cmd = MEDUSA_COMM_AUTHANSWER
    # TODO raise
    if request_id == None:
        raise(MedusaCommError)
    answer = struct.pack(med_endian.ENDIAN+"QQH", cmd, request_id, result)
    if DEBUG:
        printHex("DEBUG: answer: ", answer)
        print()

    try:
        host.write(answer)
    except OSError as err:
        print_err(err)

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
def doMedusaCommKclassdef(host):
    kclass = med_kclass.readKclassdef(host, med_endian.ENDIAN)
    # TODO: raise 'kclass already defined'
    if kclass.kclassid in hosts[host.host_name]['kclasses']:
        raise MedusaCommError
    hosts[host.host_name]['kclasses'][kclass.kclassid] = kclass
    hosts[host.host_name]['kclassesByName'][kclass.name] = kclass
    #register object
    host.hook_module.__dict__[kclass.name.title()] = kclass

#MEDUSA_COMM_KCLASSUNDEF    = 0x03 # k->c
@registerCmd(MEDUSA_COMM_KCLASSUNDEF)
def doMedusaCommKclassundef(host):
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
def doMedusaCommEvtypedef(host):
    event = readEvtypedef(host, med_endian.ENDIAN)
    # TODO: raise 'event already defined'
    if event.evid in hosts[host.host_name]['events']:
        raise MedusaCommError
    hosts[host.host_name]['events'][event.evid] = event

#MEDUSA_COMM_EVTYPEUNDEF    = 0x05 # k->c
@registerCmd(MEDUSA_COMM_EVTYPEUNDEF)
def doMedusaCommEvtypeundef(host):
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
def doMedusaCommFetchRequest(host, obj = None):
    doMedusaRequest(host, obj, MEDUSA_COMM_FETCH_REQUEST, obj.fetch_lock)
    return obj.reqAnswer

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
def doMedusaCommFetchAnswer(host):
    try:
        classid, fetch_id = struct.unpack(med_endian.ENDIAN+"QQ", host.read(8+8))
    except OSError as err:
        print_err(err)
    host.requestsAuth2Med_lock.acquire()
    obj = host.requestsAuth2Med.pop(fetch_id, None)
    host.requestsAuth2Med_lock.release()
    if obj == None:
        raise(MedusaCommError("FETCH_ANSWER: unknown FETCH_ANSWER id"))

    classType = hosts[host.host_name]['kclasses'].get(classid)
    if classType == None:
        raise(MedusaCommError("FETCH_ANSWER: unknown KCLASSID type: %x" % classid))

    try:
        obj.unpack(struct.unpack(med_endian.ENDIAN+str(classType.size)+"B", host.read(classType.size)))
    except OSError as err:
        print_err(err)

    obj.reqAnswer = MED_OK
    obj.fetch_lock.set()

'''
fetch_error message format
'''
#MEDUSA_COMM_FETCH_ERROR    = 0x09 # k->c
@registerCmd(MEDUSA_COMM_FETCH_ERROR)
def doMedusaCommFetchError(host):
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
def doMedusaCommUpdateRequest(host, obj = None):
    doMedusaRequest(host, obj, MEDUSA_COMM_UPDATE_REQUEST, obj.update_lock)
    return obj.reqAnswer

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
def doMedusaCommUpdateAnswer(host):
    try:
        classid, update_id, answer = struct.unpack(med_endian.ENDIAN+"QQI", host.read(8+8+4))
    except OSError as err:
        print_err(err)
    host.requestsAuth2Med_lock.acquire()
    obj = host.requestsAuth2Med.pop(update_id, None)
    host.requestsAuth2Med_lock.release()
    if obj == None:
        raise(MedusaCommError("UPDATE_ANSWER: unknown UPDATE_ANSWER id"))

    # next part is not necessary
    classType = hosts[host.host_name]['kclasses'].get(classid)
    if classType == None:
        raise(MedusaCommError("UPDATE_ANSWER: unknown KCLASSID type: %x" % classid))

    # write result
    obj.reqAnswer = answer
    obj.update_lock.set()

#UNKNOWN CMD
def doMedusaCommUnknown(host):
    raise( MedusaCommError() )

def print_err(err):
    for arg in err.args:
        print(arg)

def free_memory(comm):
    del hosts[comm.host_name]['kclass']
    del hosts[comm.host_name]['events']
    del hosts[comm.host_name]

'''
**************************************************************
'''

def doCommunicate(comm):
    # create namespace for 'host_name'
    hosts[comm.host_name] = dict()
    # kclasses obtained from medusa
    hosts[comm.host_name]['kclasses'] = dict()
    hosts[comm.host_name]['kclassesByName'] = dict()
    # events obtained from medusa
    hosts[comm.host_name]['events'] = dict()
    with comm as host:
        # read greeting and set byte order
        try:
            greeting = host.read(8)
        except Exception as err: #terminate this thread free hosts[comm.host_name]
            print_err(err)
            free_memory(comm)
            return -1


        end_lit = b"\x5a\x7e\x00\x66\x00\x00\x00\x00"
        end_big = b"\x00\x00\x00\x00\x66\x00\x7e\x5a"
        if greeting == end_big:
            med_endian.ENDIAN = med_endian.BIG_ENDIAN
            print("from medusa detected BIG ENDIAN byte order\n")
        elif greeting == end_lit:
            med_endian.ENDIAN = med_endian.LITTLE_ENDIAN
            print("from medusa detected LITTLE ENDIAN byte order\n")
        else:
            print("from medusa detected UNSUPPORTED byte order")
            return(-1)

        while True:
            # read next chunk of data to do
            try:
                id = struct.unpack(med_endian.ENDIAN+"Q",host.read(8))[0]
            except Exception as err: #terminate this thread free hosts[comm.host_name]
                print_err(err)
                free_memory(comm)
                return -1

            # if 'id' == 0, do (un)def kevents/kclasses...
            if id == 0:
                try:
                    cmd = host.read(4)
                except Exception as err: #terminate this thread free hosts[comm.host_name]
                    print_err(err)
                    free_memory(comm)
                    return -1

                cmd = struct.unpack(med_endian.ENDIAN+"I",cmd)[0]
                do_cmd.get(cmd, doMedusaCommUnknown)(host)
            else:
                doMedusaCommAuthrequest(host, id)
