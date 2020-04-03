#!/usr/bin/python3 

import shamir_server
import node_register
import settings


if settings.ID == 'auth':
    shamir_server.start()
else:
    node_register.start()