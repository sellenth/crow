import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import base64
import os
import hashlib

class key_holder():
    def __init__(self, key):
        self.key = key
        self.ip = "0"
        self.db = ""
        self.hash = ""


def get_keys(dbs):

    keyholder = {}
    for i in dbs:
        with open("./assets/"+i+".pub", "r") as key:
            k = key.read()   
            keyholder[i] = key_holder(RSA.importKey(k))
            keyholder[i].db = i
            keyholder[i].hash = str(base64.b64encode(hashlib.sha256(keyholder[i].key.exportKey("PEM")).digest()),'ascii')
    return keyholder

def generate_db_keys(dbs):
    for i in dbs:
        key = RSA.generate(2048, Random.get_random_bytes)
        f1 = open('./assets/'+i,'wb')
        f2 = open('./assets/'+i+'.pub','wb')
        f2.write(key.publickey().exportKey('PEM'))
        f2.close()
        f1.write(key.exportKey('PEM'))
        f1.close()

def generate_auth_keys():
    key = RSA.generate(2048, Random.get_random_bytes)
    f1 = open('./assets/auth','wb')
    f2 = open('./assets/auth.pub','wb')
    f2.write(key.publickey().exportKey('PEM'))
    f2.close()
    f1.write(key.exportKey('PEM'))
    f1.close()

def generate_device_key():
    x = str(int.from_bytes(Random.get_random_bytes(8), "big"))
    key = RSA.generate(2048, Random.get_random_bytes)
    f1 = open('./assets/local','wb')
    f2 = open('./assets/'+x+'.pub','wb')
    f3 = open('./assets/local.pub','wb')
    f2.write(key.publickey().exportKey('PEM'))
    f3.write(key.publickey().exportKey('PEM'))
    f2.close()
    f3.close()
    f1.write(key.exportKey('PEM'))
    f1.close()

def get_priv_key():
    f = open('./assets/local','r')
    x = RSA.importKey(f.read())
    f.close()
    return x

def get_keys_nodes():
    keys = []
    for i in os.listdir("./assets/hosts"):
        with open("./assets/hosts/" + i) as f:
            k = key_holder(RSA.importKey(f.read()))
            keys.append(k)
    return keys

def get_pub_key():
    f = open('./assets/local.pub','r')
    x = RSA.importKey(f.read())
    f.close()
    return x

def get_priv_key_db(db):
    f = open('./assets/'+db,'r')
    x = RSA.importKey(f.read())
    f.close()
    return x

def get_pub_key_auth():
    f = open('./assets/auth.pub','r')
    x = RSA.importKey(f.read())
    f.close()
    return x

def get_priv_key_auth():
    f = open('./assets/auth','r')
    x = RSA.importKey(f.read())
    f.close()
    return x

def encrypt_str(key, message):
    return str(base64.b64encode(key.key.publickey().encrypt(bytes(message, 'ascii'), len(message))[0]),'ascii')