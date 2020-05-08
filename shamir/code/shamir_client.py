import socket
import sqlite3
import sys
import aes_crypt
import rsa_encrypt
import settings
import threading
import numpy as np
import json
from face_recog import *


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
        incoming_embed = np.asarray(list(map(np.float,json.loads(key))))
        database_embed = np.asarray(list(map(np.float,json.loads(share["key"]))))
        num_face = share["num_faces"]
        database_embed_norm = database_embed / num_face
        dist = get_euclidian_distance(incoming_embed,database_embed_norm)
        if dist <= settings.FACE_THRESH:
            send_share(share, Host())
            conn = sqlite3.connect(settings.DBdir + settings.ID + ".db")
            c = conn.cursor()
            new_db_embed = incoming_embed + database_embed
            new_db_embed_str = json.dumps([str(i) for i in list(new_db_embed)])
            new_num_face = num_face + 1
            params = (new_db_embed_str, new_num_face, share["id"])
            c.execute('UPDATE shares SET key=?,num_faces=? WHERE id=?',params)
            
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
