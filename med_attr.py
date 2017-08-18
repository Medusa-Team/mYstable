import struct
import med_endian

MED_COMM_TYPE_END         = 0x00 # end of attribute list
MED_COMM_TYPE_UNSIGNED    = 0x01 # unsigned integer attr
MED_COMM_TYPE_SIGNED      = 0x02 # signed integer attr
MED_COMM_TYPE_STRING      = 0x03 # string attr
MED_COMM_TYPE_BITMAP      = 0x04 # bitmap attr
med_comm_type = {
    MED_COMM_TYPE_END: 'none type',
    MED_COMM_TYPE_UNSIGNED: 'unsigned',
    MED_COMM_TYPE_SIGNED: 'signed',
    MED_COMM_TYPE_STRING: 'string',
    MED_COMM_TYPE_BITMAP: 'bitmap',
}

MED_COMM_TYPE_READ_ONLY   = 0x80 # this attribute is read-only
MED_COMM_TYPE_PRIMARY_KEY = 0x40 # this attribute is used to lookup object
MED_COMM_TYPE_MASK        = 0x3f # clear read-only and primary key bits

class Attr(object):
    def __init__(self, val = None):
        self.val = val

    def __str__(self):
        s = self.name + ' = '
        # val type is SIGNED or UNSIGNED
        if type(self.val) == type(int()):
            ss = '{:0'+str(self.length)+'x}'
            s += ss.format(self.val)
        # val type is STRING
        elif type(self.val) == type(str()):
            s += "'"+self.val+"'"
        # val type is BITMAP
        elif type(self.val) == type(bytes()):
            if med_endian.ENDIAN == med_endian.BIG_ENDIAN:
                beg = 0
                end = len(self.val)
                step = 1
            elif med_endian.ENDIAN == med_endian.LITTLE_ENDIAN:
                beg = len(self.val)-1
                end = -1
                step = -1
            else:
                raise(VALUE_ERROR)
            four = 0
            for i in range(beg,end,step):
                if four == 4:
                    s += ':'
                    four = 0
                s += '{:02x}'.format(self.val[i])
                four += 1
        elif type(self.val) == type(list()):
            # val type is array of STRING
            if self.type & MED_COMM_TYPE_MASK == MED_COMM_TYPE_STRING:
                s += str(self.val)
            # val type is array of SIGNED or UNSIGNED
            else:
                for i in range(0,len(self.val)):
                    s += '{:016x}'.format(self.val[i])
                    if i < len(self.val) - 1:
                        s += ':'
        elif type(self.val) == type(None):
            s += 'Not defined yet'
        else:
            s += 'UNKNOWN ' + str(type(self.val))
        return s

''' medusa attribute definition in 'include/linux/medusa/l4/comm.h'
    struct medusa_comm_attribute_s {
    u_int16_t offset;       // offset of attribute in object
    u_int16_t length;       // bytes consumed by this attribute data in object
    u_int8_t  type;         // data type (MED_COMM_TYPE_xxx)
    char name[MEDUSA_COMM_ATTRNAME_MAX];    // string: attribute name
    }
'''
MEDUSA_COMM_ATTRNAME_MAX   = 32-5

def attributeDef(medusa, endian = "="):
    medusa_comm_attribute_s = (endian+"HHB"+str(MEDUSA_COMM_ATTRNAME_MAX)+"s", 2+2+1+MEDUSA_COMM_ATTRNAME_MAX)
    aoffset,alength,atype,aname = \
            struct.unpack(medusa_comm_attribute_s[0], \
            medusa.read(medusa_comm_attribute_s[1]))
    # finish if read end attr type
    if atype == MED_COMM_TYPE_END:
            return None
    # decode name in ascii coding
    aname = aname.decode('ascii').split('\x00',1)[0]
    # create Attr object
    #attr = Attr(aname, atype, aoffset, alength)
    attr = type(aname, (Attr,), dict())
    attr.name = aname
    attr.type = atype
    attr.offset = aoffset
    attr.length = alength

    attr.isReadonly = False
    attr.isPrimary = False
    attr.typeStr = ''         # for printing
    attr.pythonType = ''      # for struct (un)packing
    attr.afterUnpack = None   # if needed some tranformation after unpacking (i.e. for strings)
    attr.beforePack = None    # if needed some transformation before packing (i. e. for strings)

    # parse attr type and fill other Attr attributes
    atypeStr = ''
    if atype & MED_COMM_TYPE_READ_ONLY:
        atypeStr += 'readonly '
        attr.isReadonly = True
    if atype & MED_COMM_TYPE_PRIMARY_KEY:
        atypeStr += 'primary '
        attr.isPrimary = True
    # clear READ_ONLY and PRIMARY_KEY bits
    atypeStr += med_comm_type[atype & MED_COMM_TYPE_MASK]
    attr.typeStr = atypeStr

    pythonType = endian
    defaultVal = None
    if atype & MED_COMM_TYPE_MASK == MED_COMM_TYPE_SIGNED:
        # 16 bytes int only for acctype notify_change, '[a|c|m]time' attrs
        # time struct in kernel consists from two long values
        types = {'1':'b','2':'h','4':'i','8':'q','16':'2q'}
        pythonType += types[str(alength)]
        defaultVal = 0
    elif atype & MED_COMM_TYPE_MASK == MED_COMM_TYPE_UNSIGNED:
        types = {'1':'B','2':'H','4':'I','8':'Q','16':'2Q'}
        pythonType += types[str(alength)]
        defaultVal = 0
    elif atype & MED_COMM_TYPE_MASK == MED_COMM_TYPE_STRING:
        pythonType += str(alength)+'s'
        attr.afterUnpack = (lambda x, *args: ' '.join([i.decode() for i in x.split(b'\0')]).strip(),)
        attr.beforePack = (str.encode, 'ascii')
        defaultVal = ''
    elif atype & MED_COMM_TYPE_MASK == MED_COMM_TYPE_BITMAP:
        pythonType += str(alength)+'s'
        # TODO TODO TODO list of values... depending of size
        defaultVal = 0
    attr.pythonType = pythonType
    attr.defaultVal = defaultVal

    return attr

# attributes handing (pack, unpack, print format) for derived class (kclass, evtype)
class Attrs(object):
    ''' 
    initializer reads from 'medusa' interface to initialize objects values
    TODO:   create object factory for this purpose, because we need empty initializer
            for 'UPDATE' medusa command
    '''
    def __init__(self, buf=None, **kwargs):
        Attrs._unpack(self,buf)
        for k, v in kwargs.items():
            if k in self._attrDef:
                self._attr[k] = v
            else:
                raise AttributeError(k)

    def __getattr__(self, key):
        if key.startswith("_") or key in ['update', 'fetch']:
            return object.__getattr__(self, key)
        ret =  self._attr.get(key, None)
        if ret is None:
            raise AttributeError(key)
        return ret.val

    def __setattr__(self, key, val):
        if key.startswith("_") or key in ['update', 'fetch']:
            object.__setattr__(self, key, val)
            return
        ret = self._attr.get(key)
        if ret is None:
            print(self._attr)
            raise AttributeError(key)
        ret.val = val

    def _unpack(self, buf=None):
        self._orig = dict()
        for a in sorted(self._attrDef):
            attr = self._attrDef[a]
            offset = attr.offset
            length = attr.length
            data = None
            if buf != None:
                data = struct.unpack(attr.pythonType,bytes(buf[offset:offset+length]))
                self._orig[attr.name] = data
            if data and len(data) == 1:
                data = data[0]
            if data and attr.afterUnpack:
                # data can be an array (i.e. strings)
                #data = list(attr.afterUnpack[0](d,*attr.afterUnpack[1:]) for d in data.split(b'\0') if d)
                data = attr.afterUnpack[0](data,*attr.afterUnpack[1:])
                if len(data) == 1:
                    data = data[0]
            if data == None:
                data = attr.defaultVal
            self._attr[a] = attr(data)

    def _pack(self, size):
        data = bytearray(size)
        for a in sorted(self._attrDef):
            attr = self._attrDef[a]
            offset = attr.offset
            length = attr.length
            val = self._attr[a].val
            if attr.beforePack:
                val = attr.beforePack[0](val,*attr.beforePack[1:])
            struct.pack_into(attr.pythonType, data, offset, val) 
        return data

    def __str__(self):
        s = str(self.__class__) + ' = {'
        for a in sorted(self._attr):
            s += '\n\t' + str(self._attr[a])
        if self._attr:
            s += '\n'
        s += '}'

        return str(s)
