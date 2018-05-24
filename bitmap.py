import med_endian
from bitarray import bitarray
import med_endian

'''
class Bitmap - simple interface for manipulating with bitmaps

There are several possibility of initializing bitmaps:
1. Bitmap(length), where 'length' is multiple of 8
2. Bitmap(bitmap), where 'bitmap' is another bitmap
'''
class Bitmap(bitarray):
    """Class Bitmap(bitarray) for handling bitmap creation & bitmap operations
    """

    def __new__(cls, *args, **kwargs):

        if len(args) != 1:
            raise (BaseException("Bitmap constructor must have one argument"))

        if not isinstance(args[0], (Bitmap, bytes, bytearray, int)):
            raise (BaseException("Bitmap constructor arg is not a Bitmap, Bytes, Bytearray or Int object"))

        # if Bitmap is created from Int number, it represents length that must be multiple of 8
        if isinstance(args[0], int):
            if args[0] % 8:
                raise BaseException("Bitmap length must be multiple of 8")

        # create empty bitmap with given endiannes stored in **kwargs and initialize it in _init_ according to args[0]
        kwargs['endian'] = med_endian.endian_struct2bitmap[med_endian.ENDIAN]
        return super().__new__(cls, None, **kwargs)

    def __init__(self, *args, **kwargs):

        if isinstance(args[0], int):
            # initialize Bitmap instance with zeros according to Int
            # bytes(args[0]) creates given number of zero-filled bytes
            # but argument determines number of bits, not bytes -> divide by 8
            length_in_bytes = args[0] // 8
            self.frombytes(bytes(length_in_bytes))

        elif isinstance(args[0], bytes):
            # we have bytes for initialization of Bitmap
            self.frombytes(args[0])

        elif isinstance(args[0], bytearray):
            # we have bytearray for initialization of Bitmap
            self.frombytes(bytes(args[0]))

        elif isinstance(args[0], Bitmap):
            # initialize from bytes of existing Bitmap
            self.frombytes(args[0].tobytes())

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
        return self.length()

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


if __name__ == '__main__':
    import doctest
    doctest.testmod()