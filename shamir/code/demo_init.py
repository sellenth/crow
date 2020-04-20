#!/usr/bin/python3

import os
import sys
from Crypto import Random
from Crypto.PublicKey import RSA
import settings

#Grab ID
my_id = settings.ID


#Dont use this in anything you need to be secure. Please securely transport public and private keys
print("THIS SCRIPT IS ONLY FOR DEMO PURPOSES PLEASE COPY KEYS RESPONSIBLY")

#Grab list of files in assets
files = os.listdir("../assets")

#Lists of protected files in assets
protected = ["auth.pub", my_id, my_id+".pub", "local", "local.pub", "DBs", "hosts"]
protected_auth = ["auth", "auth.pub", "DBs", "hosts"]

#add variable number of databases
for i in settings.DBS:
    protected_auth.append(i+".pub")

#Dont initialize twice, it really is only to prevent duplicate local keys
if os.path.exists("../assets/initialized"):
    print("already initialized")
    exit(0)

#If a client node
if not my_id == "auth":
    
    #Remove all unprotected files
    for i in files:
        if not i in protected:
            os.remove("../assets/" + i)

    #Random number for file name
    x = str(int.from_bytes(Random.get_random_bytes(8), "big"))

    #Generate a random rsa_2048 key
    key = RSA.generate(2048, Random.get_random_bytes)
    
    #name target directory
    dirr = "../assets/"
    #open the files to store the public and private keys
    f1 = open(dirr + 'local','wb')
    f2 = open(dirr+ "hosts/" +x+'.pub','wb')
    f3 = open(dirr + 'local.pub','wb')
    
    #Export the keys
    f1.write(key.exportKey('PEM'))
    f2.write(key.publickey().exportKey('PEM'))
    f3.write(key.publickey().exportKey('PEM'))
    
    #close the files
    f2.close()
    f3.close()
    f1.close()


#if an auth node remove files not in protected_auth
else:
    for i in files:
        if not i in protected_auth:
            os.remove("../assets/" + i)

#Create the file to stop reinitialization
with open("../assets/initialized", "w") as f:
    f.write("1")
