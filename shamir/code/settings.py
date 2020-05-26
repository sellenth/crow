#Global settings variables for easy management

#List of the databases you are using
DBS = ["face", "qr", "voice", "web"]

#The identity of this node, should be auth or one of the database names
ID = 'auth'

#The total number of nodes in this system
TOTAL = 3

#The number of shares that need to be sent to authenticate a user successfully
#Changing this number will break an active system. After changing you must regenerate shares for all users.
THRESH = 3

# Used exclusively for the face DB: any distance lower than this threshold means that two faces are similar
FACE_THRESH = 0.75

#Directory locations
DBdir = "../assets/DBs/"
assetsdir = "../assets/"
#The multicast address and port to use for this system. Do not change unless you need to
MULT_ADDR = '224.3.29.1'
MULT_PORT = 13337

#Communication settings for ui
COMMS_ADDR = '224.3.29.2'
COMMS_PORT = 13338