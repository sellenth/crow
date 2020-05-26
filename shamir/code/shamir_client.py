import socket
import sqlite3
import sys
import aes_crypt
import rsa_encrypt
import settings
import json
import threading
import numpy as np
from face_recog import *
import base64
import hashlib


def challenge():

    #create host object
    host = Host()

    #Create a hash of the node's public key to send to the auth node for identity verification
    keyhash = str(base64.b64encode(hashlib.sha256(rsa_encrypt.get_pub_key().exportKey("PEM")).digest()),'ascii')
    
    #creates a payload of the message that identifies that this is a client node that needs to be updated 
    payload = "sndU"

    #create a socket to communicate with the auth nodes
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        
        #Create an empty data and address variable and a socket to recieve the data
        data = ""
        addr = 0
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as us:
            
            #set a timeout for if there is no auth node ready
            us.settimeout(1)
            us.bind(('0.0.0.0', 55551))

            #send the challenge tag to the auth nodes along with a public key to encrypt their return message with
            s.sendto(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), "who?:" + keyhash), ((host.host, host.port)))
            
            #Recv a number from the auth node to connect to
            try:
                data, addr = us.recvfrom(4096)
            #if it fails return an error
            except socket.timeout:
                us.close()
                return -1

        #Decrypt the recieved message
        data = aes_crypt.aes_dec(rsa_encrypt.get_priv_key(), data)

        #if message is bad return error
        if data == -1 or data == -2:
            return -1

        #convert data to a string to return to the auth nodes along with the instruction payload
        data = str(data, 'ascii')

        #send payload and return expected address
        s.sendto(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), "you!:" + data + ":" + payload), ((host.host, host.port)))
        return addr


#Host object to store multicast information
class Host():
    def __init__(self):
        self.host = settings.MULT_ADDR
        self.port = settings.MULT_PORT


#Send selected share to the auth node
def send_share(share, host):

    #Store the share as a string
    payload = "auth:"+ share['id'] + ":" + share['x'] + ":" + share['y']
    
    #open a socket to the multicast address
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        
        #encrypt the share with the auth public key and send it to the multicast address
        s.sendto(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), payload), ((host.host, host.port)))

    #get auth to push user updates
    try:
        challenge()

    #exit if no auth
    except:
        return


#Grab the share for a given user from the local database
def grab(user): 

    #initiate connection to the database
    conn = sqlite3.connect(settings.DBdir + settings.ID + ".db")
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()

    #Get the share associated to the provided user
    c.execute("SELECT * FROM shares WHERE id = ?", [user])
    inc = c.fetchone()
    
    #if no matching share then exit
    if inc == None:
        return -1

    #Close the connection and return the share
    conn.close()
    return inc


#authenticate the given user and key in order to send their share to the auth node
def auth_user(user, db,key):

    #Grab the user's share
    share = grab(user)
    
    #Return if error
    if share == -1:
        return

    if db == 'face':
        incoming_embed = string_to_embed(key)
        database_embed = string_to_embed(share["key"])
        num_face = database_embed[0]
        database_embed = database_embed[1:]
        database_embed_norm = database_embed / num_face
        dist = get_euclidean_distance(incoming_embed,database_embed_norm)
        if dist <= settings.FACE_THRESH:
            send_share(share, Host())
            conn = sqlite3.connect(settings.DBdir + settings.ID + ".db")
            c = conn.cursor()
            new_db_embed = incoming_embed + database_embed
            new_db_embed_str = embed_to_string(new_db_embed)
            new_num_face = (int)(num_face + 1)
            new_db_embed_str = str(new_num_face) + "," + new_db_embed_str
            params = (new_db_embed_str, share["id"])
            c.execute('UPDATE shares SET key=? WHERE id=?',params)
            
    else:

        #Make sure that the given key matches the key in the database 
        #and that the key is not null
        if key == share["key"] and not key == "":
            #Send the share if the key is valid
            send_share(share, Host())


#Recieves the user credentials from another process on the same host
#This should be sent to us from the web, qr, etc code
def recieve_creds(cli):
    
    #Recieve user:key
    try:
        #Grab key
        data = str(cli.recv(1024), 'ascii')
    
    #return if error
    except:
        cli.close()
        return 
        
    #close the connection
    cli.close()

    #Split the data
    data = data.strip("\x0a").split(":")
    
    #make sure it is correct or return error
    if not len(data) == 2:
        return -1

    #Validate
    auth_user(data[0], settings.ID, data[1])
    return


#Start a listener on the localhost so that client programs can 
#send user and  key information for validation
def start():
    
    #Create socket and bind it to localhost
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 55556))
        s.listen(5)

        #Recieve connections
        while 1 == 1:
            cli, addr = s.accept()

            #send connection to thread
            threading.Thread(target = recieve_creds, args = [cli]).start()
