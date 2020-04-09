import socket
import sqlite3
import sys
import aes_crypt
import rsa_encrypt


#Sends a string containing all relevant shares to the listening node
def send_share(key, shares, s):
  
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

    #close the databse
    conn.close()

    #connect to the secrets db
    conn = sqlite3.connect("secrets.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    #Grab all of the users to be deleted 
    c.execute("SELECT * FROM secrets WHERE timestamp > ? AND secret = ?", [float(t), "DEL"])
    users = c.fetchall()

    #Add the users to be deleted to the list
    for i in users:
        shares.append("DEL" + "|" + str(i['id']))

    #Close the connection and return
    conn.close()
    return shares


#Grabs shares created after time t and sends them to a given host
def update(key_holder, t, s):

    #Grabs shares
    shares = grab(t, key_holder.db)
    
    #sends them to the waiting node
    send_share(key_holder.key, shares, s)
