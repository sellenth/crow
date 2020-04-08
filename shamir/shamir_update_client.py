import socket
import sqlite3
import sys
import aes_crypt
import rsa_encrypt

#Host object holding the node address to connect to
class Host():
    def __init__(self, ip):
        self.host = ip
        self.port = 55588


#Sends a string containing all relevant shares to the listening node
def send_share(key, shares, host):

    #opens a socket and connects to the node
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host.host, host.port))   

        #Joins the list of shares, encrypts them with the given public key, and sends them to the listening node 
        payload = aes_crypt.aes_enc(key, ':'.join(shares))
        s.send(payload)

#grabs all shares for the provided database created after time t
def grab(t, db): 

    #initiate connection to database
    conn = sqlite3.connect(db + ".db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    #grab all shares created after time t
    c.execute("SELECT share, timestamp FROM enc_shares WHERE timestamp > ?", [float(t)])
    temp = c.fetchall()
    
    #Create a string for each share to be sent and store them in a list
    shares = []
    for i in temp:
        shares.append(i['share'] + "|" + str(i['timestamp']))

    #close the databse and return the shares
    conn.close()
    return shares


#Grabs shares created after time t and sends them to a given host
def update(key, t, host, db):

    #Grabs shares
    shares = grab(t, db)
    
    #sends them to the waiting node
    send_share(key, shares, host)
