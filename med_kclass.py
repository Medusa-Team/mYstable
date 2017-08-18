import struct
from threading import Event
from med_attr import Attrs, attributeDef, MEDUSA_COMM_ATTRNAME_MAX
import mcp

class Kclass(Attrs):
    ''' 
    initializer reads from 'medusa' interface to initialize objects values
    TODO:   create object factory for this purpose, because we need empty initializer
        for 'UPDATE' medusa command
    '''
    def __init__(self, buf=None, **kwargs):
        self._fetch_lock = Event()
        self._update_lock = Event()
        self._attr = dict()
        super(Kclass, self).__init__(buf, **kwargs)

    def fetch(self):
        self._fetch_lock.clear()
        #print('fetch: ')
        #print(self)
        return mcp.doMedusaCommFetchRequest(self._medusa, self)

    def update(self):
        self._update_lock.clear()
        #print('update: ')
        #print(self)
        return mcp.doMedusaCommUpdateRequest(self._medusa, self)

    def _pack(self):
        return super(Kclass, self)._pack(self._size)

    def _unpack(self, buf=None):
        return super(Kclass, self)._unpack(buf)

''' medusa class definition in 'include/linux/medusa/l4/comm.h'
    struct medusa_comm_kclass_s {
    u_int64_t kclassid;     // unique identifier of this kclass
    u_int16_t size;         // memory size consumed by object itself
    char name[MEDUSA_COMM_KCLASSNAME_MAX];  // string: class name
    }
'''
MEDUSA_COMM_KCLASSNAME_MAX = 32-2

'''
kclassdef message format
    size |  type                    | content
    ---------------------------------------------------
      8  |  const                   | NULL
      4  |  const                   | CLASSDEF
      ?  |  medusa_comm_kclass_s    | kclass definition
      ?  |  medusa_comm_attribute_s | attribute[]
'''
def readKclassdef(medusa, ENDIAN = "="):
    medusa_comm_kclass_s = (ENDIAN+"QH"+str(MEDUSA_COMM_KCLASSNAME_MAX)+"s", 8+2+MEDUSA_COMM_KCLASSNAME_MAX)

    kclassid, csize, cname = \
        struct.unpack(medusa_comm_kclass_s[0], \
        medusa.read(medusa_comm_kclass_s[1]))
    cname = cname.decode('ascii').split('\x00',1)[0]
    print("REGISTER class '%s' with id %0x (size = %d) {" % (cname, kclassid, csize), end='')
    #kclasses[kclassid] = {'size':csize, 'name':cname, 'attr':None}
    kclass = type(cname,(Kclass,), dict())
    kclass._kclassid = kclassid
    kclass._size = csize
    kclass._name = cname
    kclass._medusa = medusa
    kclass._attrDef = dict()

    # read attributes
    attrMaxOffset = -1
    csizeReal = 0
    attrCnt = 0
    while True:
        attr = attributeDef(medusa, ENDIAN)
        if attr == None:
            break;
        kclass._attrDef[attr.name] = attr
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
    print("")

    return kclass

