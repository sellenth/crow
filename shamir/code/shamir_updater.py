import sqlite3
import sys
import socket
import aes_crypt
import rsa_encrypt
import settings
import base64


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
    #Create empty data strings
    data = b""
    temp =""


    #Recieve data until the sender is done
    temp = cli.recv(4096)

    #repeat until done
    while not temp == "" and not len(temp) < 4096:
        data += temp
        temp = cli.recv(4096)
    
    #Add the last data string
    data += temp
        
    #close the socket
    cli.close()
    
    #get encrypted list of encrypted shares
    #ENCRYPTED_MESSAGE(ENCRYPTED_SHARES)
    #The shares are encrypted to prevent the auth node from having all knowledge
    data = aes_crypt.aes_dec(rsa_encrypt.get_priv_key(), data)
    
    #If the data is invalid return an error
    if data == -1 or data == -2:
        return -1

    #Convert data to a list
    data = str(data, 'ascii').split(":")
    
    #if no data then return
    if data == ['']:
        return 

    #For each share
    for i in data:

        #Split the share into its content and timestamp
        d = i.split("|")

        #If user is marked for deletion
        if d[0] == "DEL":

            #Delete the share and commit the action
            conn.cursor().execute("DELETE FROM shares WHERE id = ?", [d[1]])
            conn.commit()
            continue

        #decrypt the share and concatenate it with the timestamp
        temp = rsa_encrypt.get_priv_key_db(settings.ID).decrypt((base64.b64decode(d[0]),)) + b':' + bytes(d[1], 'ascii')
        
        #Pass the share into the database
        update_db(temp, conn)

    #close the connection and return the number of shares commited
    conn.close()
    return(len(data))