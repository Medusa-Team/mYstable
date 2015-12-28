''' medusa class definition in 'include/linux/medusa/l4/comm.h'
    struct medusa_comm_kclass_s {
        u_int64_t kclassid;     // unique identifier of this kclass
        u_int16_t size;         // memory size consumed by object itself
        char name[MEDUSA_COMM_KCLASSNAME_MAX];  // string: class name
    }
'''

import struct

class Kclass:
        def __init__(self, buf):
                for a in sorted(self.attr):
                        attr = self.attr[a]
                        offset = attr.offset
                        length = attr.length
                        data = struct.unpack(attr.pythonType,bytes(buf[offset:offset+length]))
                        if len(data) == 1:
                                data = data[0]
                        if attr.afterUnpack:
                                # data can be an array (i.e. strings)
                                data = list(attr.afterUnpack[0](d,*attr.afterUnpack[1:]) for d in data.split(b'\0') if d)
                                if len(data) == 1:
                                        data = data[0]
                        self.attr[a].val = data
        def __str__(self):
                s = str(self.__class__) + ' = {'
                for a in sorted(self.attr):
                        s += '\n\t' + str(self.attr[a])
                if self.attr:
                        s += '\n'
                s += '}'
                return str(s)
        def fetch(self):
                raise NotImplementedError
        def update(self):
                raise NotImplementedError

# TODO: move here from mcp.py
def appendKclass(medusa, kclassDict):
        kclassid, csize, cname = \
                struct.unpack(medusa_comm_kclass_s[0], \
                medusa.read(medusa_comm_kclass_s[1]))
        if kclassid in kclassDict:
                raise MedusaCommError
        cname = cname.decode('ascii')
        print("REGISTER class '%s' with id %0x (size = %d) {" % (cname, kclassid, csize), end='')
        #kclasses[kclassid] = {'size':csize, 'name':cname, 'attr':None}
        newkclass = type(cname,(Kclass,),{})
        newkclass.size = csize
        newkclass.name = cname
        newkclass.attr = {}
        kclassDict[kclassid] = newkclass
