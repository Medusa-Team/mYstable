MED_COMM_TYPE_END         = 0x00 # end of attribute list
MED_COMM_TYPE_UNSIGNED    = 0x01 # unsigned integer attr
MED_COMM_TYPE_SIGNED      = 0x02 # signed integer attr
MED_COMM_TYPE_STRING      = 0x03 # string attr
MED_COMM_TYPE_BITMAP      = 0x04 # bitmap attr

MED_COMM_TYPE_READ_ONLY   = 0x80 # this attribute is read-only
MED_COMM_TYPE_PRIMARY_KEY = 0x40 # this attribute is used to lookup object
MED_COMM_TYPE_MASK        = 0x3f # clear read-only and primary key bits

class Attr:
        def __init__(self,name,atype,offset,length):
                self.name = name
                self.type = atype
                self.offset = offset
                self.length = length
                self.typeStr = ''               # for printing
                self.pythonType = ''            # for struct (un)packing
                self.afterUnpack = None         # if needed some tranformation after unpacking (i.e. for strings)
                self.beforePack = None          # if needed some transformation before packing (i. e. for strings)
                self.isReadonly = False
                self.isPrimary = False
                self.val = None

        def __str__(self):
                s = self.name + ' = '
                # val type is SIGNED or UNSIGNED
                if type(self.val) == type(int()):
                        ss = '{:0'+str(self.length)+'x}'
                        s += ss.format(self.val)
                # val type is STRING
                elif type(self.val) == type(str()):
                        s += self.val
                # val type is BITMAP
                elif type(self.val) == type(bytes()):
                        for i in range(0,len(self.val)):
                                if i and i % 4 == 0:
                                        s += ':'
                                s += '{:02x}'.format(self.val[i])
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
                else:
                        s += 'UNKNOWN ' + str(type(self.val))
                return s
