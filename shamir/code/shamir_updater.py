import sqlite3
import sys
import socket
import aes_crypt
import rsa_encrypt
import settings
import base64


#deletes a user from the database if appropriate
def delete_user(conn, share):
    c = conn.cursor()

    #verify that the delete action is apprpriately timed
    c.execute("SELECT timestamp FROM shares WHERE id = ?", [share[1]])
    t = c.fetchone()

    #if timestamp does not exist delete is not new
    if t == None:
        return 0
    else: 
        t = t['timestamp']

    if float(share[2]) > t:

        #Delete the share and commit the action
        c.execute("DELETE FROM shares WHERE id = ?", [share[1]])
        conn.commit()
        return 1
    
    #delete is older than entry, will be resolvced shortly but is a true update
    else:
         return 1 


#Update share databse based on a given share string 
def update_db(data, conn):

    #Create db cursor
    c = conn.cursor()

    #Split the string into a list
    data = data.decode('utf-8').split(":")
    
    #store the list into an appropriate dictionary
    share = {}
    share['id'] = data[0]
    share['x'] = data[1]
    share['y'] = data[2]
    share['key'] = data[3]
    share['timestamp'] = data[4]

    #grab current timestamp
    c.execute("SELECT timestamp FROM shares WHERE id = ?", [share['id']])
    t = c.fetchone()

    #error handle timestamp
    if t == None:
        t = 0.0
    else: 
        t = t['timestamp']

    #verift that entry is new
    if float(share['timestamp']) > t:
        #INSERT OR REPLACE the share into the database
        c.execute("REPLACE INTO shares VALUES(?,?,?,?,?)", [share['id'], share['x'], share['y'], share['key'], share['timestamp']])
        
        #commit changes
        conn.commit()
    return

#update share database based on connecton to auth node
def update(cli):

    #open connection to local database
    conn = sqlite3.connect(settings.DBdir + settings.ID + ".db")
    conn.row_factory = sqlite3.Row
    conn.cursor().execute("CREATE TABLE IF NOT EXISTS shares(id PRIMARY KEY, x, y, key, timestamp DOUBLE)")
    conn.commit()

    #Create empty data string
    data = b""

    #Recieve until done
    try:
        while 1==1:
            temp = cli.recv(4096)
            if temp and len(temp) == 4096:
                data += temp
            else:
                break
        data += temp
    
    #if the connection dies
    except:
        #Return no updates
        return 0        
    
    #close the socket
    cli.close()
    
    #get encrypted list of encrypted shares
    #ENCRYPTED_MESSAGE(ENCRYPTED_SHARES)
    #The shares are encrypted to prevent the auth node from having all knowledge
    data = aes_crypt.aes_dec(rsa_encrypt.get_priv_key(), data)
    
    #If the data is invalid return an error
    if data == -1 or data == -2:
        print("Error in transmission, updates will be applied shortly")
        return -1

    #Convert data to a list
    data = str(data, 'ascii').split(":")

    #if no data then return
    if data == ['']:
        return 

    #record number of updates
    num_updates = len(data)

    #For each share
    for i in data:

        #Split the share into its content and timestamp
        d = i.split("|")

        #If user is marked for deletion
        if d[0] == "DEL":
            new = delete_user(conn, d)
            if not new:
                num_updates -= 1
            continue
        
        if len(d[0]) > 344:
            msg = b''
            curr_len = len(d[0])
            start = 0
            end = 344
            while curr_len > 0:
                curr_len -= 344
                dec_chunk = rsa_encrypt.get_priv_key_db(settings.ID).decrypt((base64.b64decode(d[0][start:end]),))
                msg += dec_chunk
                start += 344
                end += 344
            msg += b':' + bytes(d[1], 'ascii')
            update_db(msg,conn)
        else:

            #decrypt the share and concatenate it with the timestamp
            temp = rsa_encrypt.get_priv_key_db(settings.ID).decrypt((base64.b64decode(d[0]),)) + b':' + bytes(d[1], 'ascii')
            
            #Pass the share into the database
            update_db(temp, conn)

    #close the connection and return the number of shares commited
    conn.close()
    return num_updates