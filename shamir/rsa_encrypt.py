import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import base64
import os
import hashlib


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

        #open the public key file
        with open("./assets/"+i+".pub", "r") as key:
            
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
        f1 = open('./assets/'+i,'wb')
        f2 = open('./assets/'+i+'.pub','wb')

        #export the keys
        f2.write(key.publickey().exportKey('PEM'))
        f1.write(key.exportKey('PEM'))

        #Close files
        f2.close()
        f1.close()

#Generate auth keys for a system
def generate_auth_keys():

    #Create Random rsa_2048 key
    key = RSA.generate(2048, Random.get_random_bytes)
    
    #open files for public and private keys
    f1 = open('./assets/auth','wb')
    f2 = open('./assets/auth.pub','wb')

    #Export the keys
    f2.write(key.publickey().exportKey('PEM'))
    f1.write(key.exportKey('PEM'))
    
    #close the key files
    f2.close()
    f1.close()


#Generate device keys for a node (only used for auth node if anticipating changing it to a client node at some point)
def generate_device_key():
    
    #Generate a random file name to store the public key on the auth node
    x = str(int.from_bytes(Random.get_random_bytes(8), "big"))

    #Generate a random rsa_2048 key
    key = RSA.generate(2048, Random.get_random_bytes)
    
    #open the files to store the public and private keys
    f1 = open('./assets/local','wb')
    f2 = open('./assets/'+x+'.pub','wb')
    f3 = open('./assets/local.pub','wb')
    
    #Export the keys
    f1.write(key.exportKey('PEM'))
    f2.write(key.publickey().exportKey('PEM'))
    f3.write(key.publickey().exportKey('PEM'))
    
    #close the files
    f2.close()
    f3.close()
    f1.close()


#Grab device private key
def get_priv_key():

    #open file
    f = open('./assets/local','r')
    
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
    for i in os.listdir("./assets/hosts"):

        #Open the file
        with open("./assets/hosts/" + i) as f:
            
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

    #open file
    f = open('./assets/local.pub','r')
    
    #import key
    x = RSA.importKey(f.read())
    
    #close file and return key
    f.close()
    return x


#Get the private key for the local database
def get_priv_key_db(db):

    #open the file based on the settings file
    f = open('./assets/'+db,'r')

    #import the key
    x = RSA.importKey(f.read())
    
    #close the key file and return the key
    f.close()
    return x

#Get the auth public key 
def get_pub_key_auth():

    #open the file
    f = open('./assets/auth.pub','r')
    
    #import the key
    x = RSA.importKey(f.read())
    
    #close the file and return the key
    f.close()
    return x


#Get the auth node private key
def get_priv_key_auth():
    
    #open the file
    f = open('./assets/auth','r')
    
    #import the key
    x = RSA.importKey(f.read())
    
    #return the key
    f.close()
    return x

#Grabs a hash of the auth private key
def get_auth_hash():

    #Open auth private key file
    f = open("./assets/auth", "r")

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