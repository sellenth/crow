#!/usr/bin/python3

import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import base64
import os
import hashlib
import settings


#Class to hold key information
class key_holder():
    def __init__(self, key):
        self.key = key
        self.db = ""
        self.hash = ""


#Grabs the public keys from each database and returns them in a dictionary
def get_keys(dbs):

    #Create dictionary to hold the keys
    keyholder = {}

    #for each database
    for i in dbs:

        #make sure keys exist
        if not os.path.exists(settings.assetsdir + i + ".pub"):
            print("Please run ./rsa_encrypt.py and generate db keys!")
            exit(0)

        #open the public key file
        with open(settings.assetsdir +i+".pub", "r") as key:
            
            #read the key into the dictionary
            k = key.read()
            keyholder[i] = key_holder(RSA.importKey(k))
            
            #Mark the key with the proper db name in case it is passed into functions
            keyholder[i].db = i
    
    #return dictionary
    return keyholder


#Generates database keys for a system
def generate_db_keys(dbs):

    #for each database
    for i in dbs:

        #Generate a random rsa_2048 key
        key = RSA.generate(2048, Random.get_random_bytes)
        
        #Open files for the public and private keys
        f1 = open(settings.assetsdir + i,'wb')
        f2 = open(settings.assetsdir + i+'.pub','wb')

        #export the keys
        f2.write(key.publickey().exportKey('PEM'))
        f1.write(key.exportKey('PEM'))

        #Close files
        f2.close()
        f1.close()
    return


#Generate auth keys for a system
def generate_auth_keys():

    #Create Random rsa_2048 key
    key = RSA.generate(2048, Random.get_random_bytes)
    
    #open files for public and private keys
    f1 = open(settings.assetsdir + 'auth','wb')
    f2 = open(settings.assetsdir + 'auth.pub','wb')

    #Export the keys
    f2.write(key.publickey().exportKey('PEM'))
    f1.write(key.exportKey('PEM'))
    
    #close the key files
    f2.close()
    f1.close()
    return


#Generate device keys for a node (only used for auth node if anticipating changing it to a client node at some point)
def generate_device_key():
    
    #Generate a random file name to store the public key on the auth node
    x = str(int.from_bytes(Random.get_random_bytes(8), "big"))

    #Generate a random rsa_2048 key
    key = RSA.generate(2048, Random.get_random_bytes)
    
    #Generate comms number
    comms_number = int.from_bytes(Random.get_random_bytes(8), "big")
    comms_number = str(comms_number)
    with open(settings.assetsdir + "comms_number", "w") as c:
        c.write(comms_number)

    #open the files to store the public and private keys
    f1 = open(settings.assetsdir + 'local','wb')
    f2 = open(settings.assetsdir+ "hosts/" +x+'.pub','wb')
    f3 = open(settings.assetsdir + 'local.pub','wb')
    
    #Export the keys
    f1.write(key.exportKey('PEM'))
    f2.write(key.publickey().exportKey('PEM'))
    f3.write(key.publickey().exportKey('PEM'))
    
    #close the files
    f2.close()
    f3.close()
    f1.close()
    return


#Grab device private key
def get_priv_key():

    #make sure key exists
    if not os.path.exists(settings.assetsdir + 'local'):
        print("Please generate a local key with ./rsa_encrypt option 1")
        exit(0)


    #open file
    f = open(settings.assetsdir + 'local','r')
    
    #import key
    x = RSA.importKey(f.read())
    
    #close file and return key object
    f.close()
    return x


#Grabs the public key for each client node and returns them in a list
def get_keys_nodes():

    #Create list object
    keys = []

    #For each file in the /assets/hosts directory
    for i in os.listdir(settings.assetsdir +  "hosts"):

        #Open the file
        with open(settings.assetsdir +  "hosts/" + i) as f:
            
            #dont import readme
            if i == "README":
                continue

            #import the key
            k = key_holder(RSA.importKey(f.read()))
            
            #record the hash of the key for later ease of authentication
            k.hash = str(base64.b64encode(hashlib.sha256(k.key.exportKey("PEM")).digest()),'ascii')

            #Append the key to the list
            keys.append(k)

    #return the keys
    return keys


#Get the public key for the current device
def get_pub_key():

    #make sure key exists
    if not os.path.exists(settings.assetsdir + 'local.pub'):
        print("Please generate a local key with ./rsa_encrypt option 1")

    #open file
    f = open(settings.assetsdir + 'local.pub','r')
    
    #import key
    x = RSA.importKey(f.read())
    
    #close file and return key
    f.close()
    return x


#Get the private key for the local database
def get_priv_key_db(db):

    #make sure key exists
    if not os.path.exists(settings.assetsdir + db):
        print("Please generate and/or import the database keys")
        exit(0)

    #open the file based on the settings file
    f = open(settings.assetsdir + db,'r')

    #import the key
    x = RSA.importKey(f.read())
    
    #close the key file and return the key
    f.close()
    return x

#Get the auth public key 
def get_pub_key_auth():

    #make sure key exists
    if not os.path.exists(settings.assetsdir + "auth.pub"):
        print("Please generate and/or import the auth public key")
        exit(0)

    #open the file
    f = open(settings.assetsdir + 'auth.pub','r')
    
    #import the key
    x = RSA.importKey(f.read())
    
    #close the file and return the key
    f.close()
    return x


#Get the auth node private key
def get_priv_key_auth():
    
    #make sure key exists
    if not os.path.exists(settings.assetsdir + "auth"):
        print("Please generate and/or import the auth keys")
        exit(0)

    #open the file
    f = open(settings.assetsdir + 'auth','r')
    
    #import the key
    x = RSA.importKey(f.read())
    
    #return the key
    f.close()
    return x

#Grabs a hash of the auth private key
def get_auth_hash():

    #make sure key exists
    if not os.path.exists(settings.assetsdir + "auth"):
        print("Please generate and/or import the auth keys")
        exit(0)

    #Open auth private key file
    f = open(settings.assetsdir +  "auth", "r")

    #Grab hash of the file
    h = base64.b64encode(hashlib.sha256(bytes(f.read(), 'ascii')).digest())

    #close file
    f.close()

    #return the hash as a string
    return str(h, 'ascii')

#encrypt a string using an rsa private key given the key and a string
def encrypt_str(key, message):

    #return an encrypted string encoded with base64
    return str(base64.b64encode(key.publickey().encrypt(bytes(message, 'ascii'), len(message))[0]),'ascii')


#Tool to create keys
if __name__ == "__main__":
    
    #handle for user error
    try:
        #print menu and direct user to the action they need
        print ("Generate device key\t(1):\n\nGenerate DB Keys\t(2):\n\nGenerate auth keys\t(3):\n")
        choice = int(input())
        if choice == 1:
            generate_device_key()
        if choice == 2:
            generate_db_keys(settings.DBS)
        if choice == 3:
            generate_auth_keys()

        #let user know task is done, db_key generation can take a few seconds
        print("Done!, thanks")
    
    #be nice to user
    except:
        print("There was an error, maybe you pressed the wrong button")        