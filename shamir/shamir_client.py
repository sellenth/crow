import socket
import sqlite3
import sys
import aes_crypt
import rsa_encrypt
import settings


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
    conn = sqlite3.connect(settings.ID + ".db")
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()

    #Get the share associated to the provided user
    c.execute("SELECT * FROM shares WHERE id = ?", [user])
    inc = c.fetchone()
    
    #Close the connection and return the share
    conn.close()
    return inc


#authenticate the given user and key in order to send their share to the auth node
def auth_user(user, db,key):

    #Grab the user's share
    share = grab(user)
    
    #Make sure that the given key matches the key in the database 
    #and that the key is not null
    print(share['id'])
    print(key)
    print(share["key"])
    print(key == share["key"])
    if key == share["key"] and not key == "":
        
        #Send the share if the key is valid
        send_share(share, Host())


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
            
            #Recieve user:key 
            data = str(cli.recv(1024), 'ascii')
            
            #close the connection
            cli.close()

            #Split the data and send it to the validator
            data = data.split(":")
            auth_user(data[0], settings.ID, data[1])

            
