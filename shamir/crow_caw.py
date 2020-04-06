#!/usr/bin/python3 

import shamir_server
import node_register
import settings


if settings.ID == 'auth':
    print("a")
    shamir_server.start()
else:
    print("b")
    node_register.start()