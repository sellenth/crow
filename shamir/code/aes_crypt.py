import rsa_encrypt
import settings
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import os
import base64
import time
import hashlib

#encrypts a mesage via AES dependant upon a rsa public key
#leaving a timestamp on the message as well as a hash of the content
#secured by the rsa key
#RSA(AES_key, Hash_of_message_and_timestamp) || AES(timestamp, message)
#takes as input a key and a string, returns bytes for send()
def aes_enc(rsa_key, message):

    #generate random key and iv
    k = os.urandom(32)
    iv = os.urandom(16)

    #append timestamp to message
    message = str(time.time()) + "|||" + message

    #pad message with 0 bytes to match block size
    message = message + "\x00" * (16 - (len(message) % 16))
    
    #Create AES object with key and iv
    Cip = AES.new(k, AES.MODE_CBC, iv) 

    #encrypt the timestamp || message   
    x = Cip.encrypt(message)
    
    #prepend iv to message
    payload = bytes(iv) + x

    #Create hash of message
    mac = hashlib.sha256(payload)
    mac = mac.digest()

    #encrypt the key k and the hash of the message via the rsa key
    #then encode them via base64 for readability and ease of use
    hmac = rsa_key.publickey().encrypt(k+mac, len(mac) +32)[0]
    hmac = base64.b64encode(hmac)

    #encode the ciphertext with base64
    payload = base64.b64encode(payload)

    #return the MAC prepended to the payload
    return hmac + b':' + payload


#Decrypts a message by recovering a AES key, and message hash dependant on an RSA private key
#Validates the message hash, then the timestamp contained within the message to make sure that it was sent recently
#Takes as input a key and bytes (meant to be the output of recv(), returns bytes as well
def aes_dec(rsa_key, ciphertext):
    #split the message into key||mac and ciphertext
    cip = ciphertext.split(b':')
    
    #If invalid ciphertext than exit
    if not len(cip) == 2:
        print("length:   " + str(cip))
        return -1

    #Grab MAC
    hmac = cip[0]
    #grab ciphertext
    cip = cip[1]
    
    #decoode ciphertext and hmac so that they can be decrypted
    cip = base64.b64decode(cip)
    hmac = base64.b64decode(hmac)

    #decrypt the hmac with the given RSA private key
    hmac = rsa_key.decrypt((hmac,))

    #split the key and hash
    key = hmac[0:32]
    hsh = hmac[32:]

    #validate that the message hash matches the hash given
    if(hsh == hashlib.sha256(cip).digest()):

        #decrypt the AES encrypted message
        Cip = AES.new(key, AES.MODE_CBC, cip[0:16])
        cip = Cip.decrypt(cip)
        
        #strip padding and IV from message
        message = cip[16:].strip(b'\x00')

        #split into time||message into message and timestamp
        message = message.split(b"|||")
        
        #make sure that the message was sent recently
        if time.time() - float(str(message[0], 'ascii')) < 1:
            
            #if so return the message
            return message[1]
        else:
            #otherwise error for timestamp
            return -2
   
    else:
        #return error for hash mismatch
        print("Hash:  "  + str(cip))
        return -1