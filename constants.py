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
