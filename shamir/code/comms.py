import settings
import socket
import struct
import threading
import json
import aes_crypt
import rsa_encrypt
import base64
import hashlib
import time
import sqlite3
import sys



def initialize_db():
    conn = sqlite3.connect(settings.DBdir + "UI.db")
    conn.row_factory = sqlite3.Row
    conn.cursor().execute("PRAGMA recursive_triggers='ON'")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS nodes(type, id PRIMARY KEY, timestamp DOUBLE)")
    c.execute("CREATE TABLE IF NOT EXISTS totals(type PRIMARY KEY, number)")
    c.execute("CREATE TRIGGER IF NOT EXISTS tally_upd AFTER UPDATE ON nodes BEGIN " + 
        "REPLACE INTO totals VALUES(new.type, (SELECT COUNT(*) FROM nodes WHERE type = new.type));" +
        "REPLACE INTO totals VALUES(old.type, (SELECT COUNT(*) FROM nodes WHERE type = old.type)); END;"
    )

    c.execute("CREATE TRIGGER IF NOT EXISTS tally_ins AFTER INSERT ON nodes BEGIN " + 
        "REPLACE INTO totals VALUES(new.type, (SELECT COUNT(*) FROM nodes WHERE type = new.type)); END;"
    )

    c.execute("CREATE TRIGGER IF NOT EXISTS tally_del AFTER DELETE ON nodes BEGIN " + 
        "REPLACE INTO totals VALUES(old.type, (SELECT COUNT(*) FROM nodes WHERE type = old.type)); END;"
    )
    conn.commit()


def send(message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        s.sendto(bytes(message, 'ascii'), (settings.COMMS_ADDR, settings.COMMS_PORT))


def handle(mess, addr):
    mess = json.loads(mess)
    if mess['action'] == "newDB":
        print("New DB Ready")

    elif mess['action'] == "newUser":
        print("New user share")    
    
    elif mess['action'] == "update_dbs":

        print("Recieved DBs:")
        for i in mess["clients"]:
            print(i["database"] + " " + str(i["number"]))

    elif mess['action'] == "update_users":
        
        print("Recieved Users:")
        for i in mess["users"]:
            print(i["user"] + " " + str(i["num_shares"]))

    elif mess['action'] == "update_all":
        
        print("Recieved Total update\n")
        print("Recieved DBs:")
        for i in mess["clients"]:
            print(i["database"] + " " + str(i["number"]))  

        print("\nRecieved Users:")
        for i in mess["users"]:
            print(i["user"] + " " + str(i["num_shares"]))


def database_log(data):

    conn = sqlite3.connect(settings.DBdir + "UI.db")
    conn.row_factory = sqlite3.Row
    conn.cursor().execute("PRAGMA recursive_triggers='ON'")
    c = conn.cursor()
    c.execute("REPLACE INTO nodes VALUES(?,?, ?)", data)

    c.execute("SELECT * FROM nodes")
    nodes = c.fetchall()

    if not nodes == None:
        for i in nodes:
            if (time.time() - i['timestamp'])  > 300:
                c.execute("DELETE FROM nodes WHERE id = ?", [i['id']])

    conn.commit()
    conn.close()

def send_clients_full(addr):
    conn = sqlite3.connect(settings.DBdir + "UI.db")
    conn.row_factory = sqlite3.Row
    conn.cursor().execute("PRAGMA recursive_triggers='ON'")
    c = conn.cursor()

    c.execute("SELECT * FROM nodes")
    nodes = c.fetchall()

    payload = {}
    payload['payload'] = []

    if not nodes == None:
        for i in nodes:
            payload['payload'].append({"type":i["type"], "id":i['id'], "timestamp":i['timestamp']})

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((addr, 55559))
        s.send(bytes(json.dumps(payload), 'ascii'))

def communicator(payload):

    #create a socket to communicate with the auth nodes
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

        #Create a hash of the node's public key to send to the auth node for identity verification
        keyhash = str(base64.b64encode(hashlib.sha256(rsa_encrypt.get_pub_key().exportKey("PEM")).digest()),'ascii')
        
        #Create an empty data and address variable and a socket to recieve the data
        data = ""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as us:
            
            #set a timeout for if there is no auth node ready
            us.settimeout(1)
            us.bind(('0.0.0.0', 55551))

            #send the challenge tag to the auth nodes along with a public key to encrypt their return message with
            s.sendto(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), "who?:" + keyhash), ((settings.MULT_ADDR, settings.MULT_PORT)))
            
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
        s.sendto(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), "you!:" + data + ":" + payload), ((settings.MULT_ADDR, settings.MULT_PORT)))


def send_clients():
    payload = ""
    conn = sqlite3.connect(settings.DBdir + "UI.db")
    conn.row_factory = sqlite3.Row
    conn.cursor().execute("PRAGMA recursive_triggers='ON'")
    c = conn.cursor()
    c.execute("SELECT * FROM totals")

    clients = c.fetchall()
    if clients == None:
        payload = json.dumps({"action":"err"})

    cliDict = {"action":"update_dbs"}
    cliDict["clients"] = []

    for i in clients:
        
        if i["number"] == 0:
            continue

        cliDict['clients'].append({"database":i['type'], "number":i['number']})

    payload = json.dumps(cliDict)

    conn.close()

    send(payload)


def send_users():
    payload = ""
    conn = sqlite3.connect(settings.DBdir + "shares.db")
    conn.row_factory = sqlite3.Row
    conn.cursor().execute("PRAGMA recursive_triggers='ON'")   
    c = conn.cursor()

    c.execute("SELECT * FROM shares")

    clients = c.fetchall()
    if clients == None:
        payload = json.dumps({"action":"err"})

    usrDict = {"action":"update_users"}
    usrDict["users"] = []

    for i in clients:
        if (time.time()) - i['timestamp'] > 60:
            continue
        usrDict['users'].append({"user":i['id'], "num_shares":i['num_shares']})

    payload = json.dumps(usrDict)

    conn.close()

    send(payload)



def send_both():

    payload = ""
    
    conn = sqlite3.connect(settings.DBdir + "UI.db")
    conn.row_factory = sqlite3.Row
    conn.cursor().execute("PRAGMA recursive_triggers='ON'")
    c = conn.cursor()
    c.execute("SELECT * FROM totals")

    clients = c.fetchall()
    if clients == None:
        payload = json.dumps({"action":"err"})

    cliDict = {"action":"update_all"}
    cliDict["clients"] = []

    for i in clients:

        if i["number"] == 0:
            continue

        cliDict['clients'].append({"database":i['type'], "number":i['number']})

    conn.close()


    payload = ""
    conn = sqlite3.connect(settings.DBdir + "shares.db")
    conn.row_factory = sqlite3.Row
    conn.cursor().execute("PRAGMA recursive_triggers='ON'")   
    c = conn.cursor()
    c.execute("SELECT * FROM shares")

    clients = c.fetchall()
    if clients == None:
        payload = json.dumps({"action":"err"})

    cliDict["users"] = []

    for i in clients:
        if (time.time()) - i['timestamp'] > 60:
            continue
        cliDict['users'].append({"user":i['id'], "num_shares":i['num_shares']})

    payload = json.dumps(cliDict)

    send(payload)

    conn.close()


def run_server():

    initialize_db()

    address = settings.COMMS_ADDR
    port = settings.COMMS_PORT 
    tup = ('', port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(tup)
    group = socket.inet_aton(address)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while(1):
        mess, addr = s.recvfrom(4096)
        mess = str(mess, 'ascii')

        threading.Thread(target=handle, args=[mess, addr]).start()

if __name__ == "__main__":
    communicator(sys.argv[1])