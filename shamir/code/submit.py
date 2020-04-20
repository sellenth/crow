#!/usr/bin/python3

import socket
import settings

#This program sends user input to the local client to authenticate
if __name__ == "__main__":
    
    #exit if auth node
    if settings.ID == 'auth':
        print("this is for client nodes, sorry")
        exit(0)

    #open socket to client
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 55556))

        #Grab info
        print("Username: ")
        usr = input().strip("\n")
        print("Password for " + settings.ID + " DB: ")
        pas = input().strip("\n")

        #Send info
        s.send(bytes(usr + ":" + pas, 'ascii'))

        #Exit message
        print("\nSent! Thanks for flying Crow!")
        exit(0)
