#!/usr/bin/python3

import shamir
import sqlite3
import rsa_encrypt
import time
import base64
import settings


#Class to hold the database 
class db:
    name = ""
    key = ""
    def __init__(self):
        self.name = ""
        self.key = ""


#add user secret to the secrets database
def add_secret(username, name, secret, currtime):
    
    #initiate database connection
    conn = sqlite3.connect(settings.DBdir + "secrets.db")
    c = conn.cursor()

    #make sure table exists
    c.execute("CREATE TABLE IF NOT EXISTS secrets(id PRIMARY KEY, name, secret, timestamp DOUBLE)")
    
    #INSERT OR REPLACE into secrets the secret and user info
    c.execute("REPLACE INTO secrets VALUES (?,?,?,?)", [username, name, str(secret), currtime])
    
    #commit and close connection
    conn.commit()
    conn.close()
    return


#Encrypt shares with db_keys and store them into their respective databases
def add_shares(username, shares, keys, currtime):
    
    #Grab database keys
    db_keys = rsa_encrypt.get_keys(settings.DBS)
    
    #shares must be equal to dbs to prevent loss or oversharing
    if((not len(shares) == len(settings.DBS))):
        return -1

    #For each database
    for i in range(len(settings.DBS)):
        
        #initiate database connection
        conn = sqlite3.connect(settings.DBdir + settings.DBS[i] + ".db")
        c = conn.cursor()

        #make sure the shares table exists
        create = "CREATE TABLE IF NOT EXISTS enc_shares(id PRIMARY KEY, share, timestamp DOUBLE)"
        c.execute(create)
        
        #Convert share data to a string
        payload = username + ":" + str(shares[i][0])  + ":" + str(shares[i][1]) + ":" + str(keys[i])

        # if the string is longer than a sha256 hash, chunk the string and encrypt each chunk individually
        if len(payload) > 240:

            # store the individual chunks
            chunks = []
            curr_len = len(payload)
            start = 0
            end = 240
            while curr_len > 240:

                # decrement the curr_len to indicate that a chunk has been encrypted
                curr_len -= 240

                # append a chunk of the payload 
                chunks.append(payload[start:end])
                start += 240
                end += 240

            #append the last chunk to the chunks list
            chunks.append(payload[start:])
            k = db_keys[settings.DBS[i]].key
            chunk_payload = ""

            # encrypt each chunk in the payload
            for chunk in chunks:
                chunk_payload += rsa_encrypt.encrypt_str(k, chunk)
            c.execute("REPLACE INTO enc_shares VALUES(?, ?, ?)", [username, chunk_payload, currtime])
        else:
        
            #Grab the database key for the current database
            k = db_keys[settings.DBS[i]].key
            
            #encrypt the share string with the database public key
            payload = rsa_encrypt.encrypt_str(k, payload)

            #insert or replace the encrypted share, the username, and a timestamp into the database
            c.execute("REPLACE INTO enc_shares VALUES(?, ?, ?)", [username, payload, currtime])
        
        #commit the action and close the database
        conn.commit()
        conn.close()
    return


#Generate the secrets for the sharing scheme to use
def gen_secrets(username, name, keys):

    #Validate that there are enough databases
    if(len(settings.DBS) < settings.TOTAL) or len(keys) < settings.TOTAL:
        return -1
    
    #Generate the secret and shares
    secret, shares = shamir.make_random_shares(settings.THRESH, settings.TOTAL)
    
    #Grab a timestamp
    currtime = time.time()

    #add the secret to the secrets database
    add_secret(username, name, secret, currtime)

    #add encrypted shares to the shares db
    add_shares(username, shares, keys, currtime)
    return


#add a user to the system given a username, name, and key list
def add_user(username, name, keys_list):
     
    #make sure that all keys are non-null
    for i in keys_list: 
        if i == "":
            return -1
    
    #generate the user
    gen_secrets(username, name, keys_list)
    return

#if run as main
if __name__ == "__main__":

    #Exit if client node
    if not settings.ID == 'auth':
        print("run this on an auth node")
        exit(0)

    #Add test users
    add_user("r3k", "Ryan Kennedy", ["111111"] * settings.TOTAL)
    add_user("hal", "Halston Sellentin", ["111111"] * settings.TOTAL )