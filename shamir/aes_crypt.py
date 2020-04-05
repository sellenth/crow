import rsa_encrypt
import settings
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import os
import base64
import time
import hashlib

def aes_enc(rsa_key, message):
    k = os.urandom(32)
    iv = os.urandom(16)
    message = str(time.time()) + "|||" + message
    message = message + "\x00" * (16 - (len(message) % 16))
    Cip =AES.new(k, AES.MODE_CBC, iv)    
    x = Cip.encrypt(message)
    payload = bytes(iv) + x
    mac = hashlib.sha256(payload)
    mac = mac.digest()
    hmac = rsa_key.publickey().encrypt(k+mac, len(mac) +32)[0]
    hmac = base64.b64encode(hmac)
    payload = base64.b64encode(payload)
    return hmac + b':' + payload

def aes_dec(rsa_key, ciphertext):
    cip = ciphertext.split(b':')
    hmac = cip[0]
    cip = cip[1]
    cip = base64.b64decode(cip)
    hmac = base64.b64decode(hmac)
    hmac = rsa_key.decrypt((hmac,))
    key = hmac[0:32]
    hsh = hmac[32:]
    if(hsh == hashlib.sha256(cip).digest()):
        Cip = AES.new(key, AES.MODE_CBC, cip[0:16])
        cip = Cip.decrypt(cip)
        
        message = cip[16:].strip(b'\x00')
        message = message.split(b"|||")
        if time.time() - float(str(message[0], 'ascii')):
            return message[1]
        else:
            return -2
    else:
        return -1

