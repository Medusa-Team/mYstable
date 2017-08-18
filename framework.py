import med_endian

'''
class Bitmap - simple interface for manipulating with bitmaps

There are several possibility of initializing bitmaps:
1. Bitmap(length), where 'length' is multiple of 8
2. Bitmap(bitmap), where 'bitmap' is another bitmap
'''
class Bitmap(bytearray):
    def __init__(self, *args, **kwargs):
        if len(args) != 1:
            raise(BaseException("Bitmap constructor must have one argument"))
        if not isinstance(args[0], (type(self), bytes, bytearray, int)):
            raise(BaseException("Bitmap constructor arg is not a Bitmap, Bytes, Bytearray or Int object"))

        # determine bitmap length and initializer by int
        if isinstance(args[0], int):
            if args[0] % 8:
                raise(BaseException("Bitmap length must be multiply of 8"))
            self.len = args[0]
            args = [bytes(self.len//8),]
        # determine bitmap length and initializer by another bitmap
        elif isinstance(args[0], type(self)):
            self.len = args[0].len
            #args = [bytes(self.len//8),]
        # determine bitmap length and initializer by another bitmap
        elif isinstance(args[0], (bytes, bytearray)):
            self.len = len(args[0]) * 8
            
        super(Bitmap, self).__init__(*args, **kwargs)

    def __str__(self, separator=':'):
        s = ''
        if med_endian.ENDIAN == med_endian.BIG_ENDIAN:
            beg = 0
            end = super(Bitmap, self).__len__()
            step = 1
        elif med_endian.ENDIAN == med_endian.LITTLE_ENDIAN:
            beg = super(Bitmap, self).__len__() - 1
            end = -1
            step = -1
        else:
            raise(BaseException("Bitmap.__str__(): Unknown endianness"))
        four = 0
        for i in range(beg,end,step):
            if separator != None and four == 4:
                s += separator
                four = 0
            s += '{:02x}'.format(super(Bitmap, self).__getitem__(i))
            four += 1
        return s

    # length of bitmap is len(bytearray) * 8
    def __len__(self):
        return self.len

    # get i-th bit of bitmap
    #def __getitem__(self, key):
    #    val = super(Bitmap, self).__getitem__(key//8)
    #    val = (val >> (key % 8)) & 0x01
    #    #print("Bitmap __getitem(%d) = %d" % (key, val))
    #    return val

    # set i-th bit of bitmap
    #def __setitem__(self, key, val):
    #    raise(BaseException("Not implemented yet"))

    def set(self):
        for item, val in enumerate(self):
            self[item] = 0xff

    def clear(self):
        for item, val in enumerate(self):
            self[item] = 0x00

class Register():
    def __init__(self):
        self.hooks = {}

    def __call__(self, evname, **kwargs):
        def register_decorator(func):
            hooks = self.hooks.setdefault(evname, [])
            hooks.append({'exec': func,
                          'event': kwargs.get('event'),
                          'object': kwargs.get('object'),
                          'subject': kwargs.get('subject')})
            return func
        return register_decorator

def exec(cmd, obj):
    # execute function
    if callable(cmd):
        return cmd(obj)
    #conpare dictionaries
    if isinstance(cmd, dict):
        #print('compare dictionaries')
        for k, v in cmd.items():
            if not exec(v, obj.__getattr__(k)):
                False
        return True
    if isinstance(cmd, list):
        # compare lists
        if isinstance(obj, list):
            if len(cmd) != len(obj):
               return False
            for i in range(len(cmd)):
               if not exec(cmd[i], obj.__getattr__(i)):
                  return False
            return True
        # this is OR
        for i in cmd:
            if exec(i, obj):
                return True
        return False
    # and compare
    return cmd == obj

class Xor:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __call__(self, obj):
        return exec(self.a, obj) ^ exec(self.b, obj)

class Not:
    def __init__(self, arg):
        self.arg = arg
    def __call__(self, val):
        return not exec(self.arg, val)

class And:
    def __init__(self, *args):
        self.args = args
    def __call__(self, obj):
        for i in self.args:
            if not exec(i, obj): return False
        return True

class Or:
    def __init__(self, *args):
        self.args = args
    def __call__(self, obj):
        for i in self.args:
            if exec(i, obj): return True
        return False

class Dividable:
    def __init__(self, val):
        self.val = val
    def __call__(self, val):
        return self.val % val == 0

class Ge:
    def __init__(self, val):
        self.val = val
    def __call__(self, val):
        return self.val <= val

class Gt:
    def __init__(self, val):
        self.val = val
    def __call__(self, val):
        return self.val < val

class Le:
    def __init__(self, val):
        self.val = val
    def __call__(self, val):
        return self.val >= val

class Lt:
    def __init__(self, val):
        self.val = val
    def __call__(self, val):
        return self.val > val

class Between:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __call__(self, val):
        return self.a <= val and val <= self.b
