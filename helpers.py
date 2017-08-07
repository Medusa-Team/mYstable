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

