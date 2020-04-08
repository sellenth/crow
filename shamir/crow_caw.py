#!/usr/bin/python3 

import shamir_server
import node_register
import settings

#If the node is listed as an auth node then start the auth server
#Otherwise start the client node program
if settings.ID == 'auth':
    shamir_server.start()
else:
    node_register.start()