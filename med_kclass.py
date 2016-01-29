import struct
from med_attr import Attr, AttrInit, readAttribute, MEDUSA_COMM_ATTRNAME_MAX

class Kclass(AttrInit):
        ''' 
        initializer reads from 'medusa' interface to initialize objects values
        TODO:   create object factory for this purpose, because we need empty initializer
                for 'UPDATE' medusa command
        '''
        def __init__(self, buf):
                AttrInit.__init__(self, buf)
        def fetch(self):
                # TODO TODO TODO
                raise NotImplementedError
        def update(self):
                # TODO TODO TODO
                raise NotImplementedError

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
        def __init__(self, buf):
                Kclass.__init__(self, buf)

        kclassid, csize, cname = \
                struct.unpack(medusa_comm_kclass_s[0], \
                medusa.read(medusa_comm_kclass_s[1]))
        cname = cname.decode('ascii').split('\x00',1)[0]
        print("REGISTER class '%s' with id %0x (size = %d) {" % (cname, kclassid, csize), end='')
        #kclasses[kclassid] = {'size':csize, 'name':cname, 'attr':None}
        kclass = type(cname,(Kclass,),dict(__init__ = __init__))
        kclass.kclassid = kclassid
        kclass.size = csize
        kclass.name = cname
        kclass.attr = dict()

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
        print("")

        return kclass

