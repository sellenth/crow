import settings
import socket
import struct
import threading
import json
import aes_crypt
import rsa_encrypt
import base64
import hashlib
import sqlite3

conn = sqlite3.connect("UI.db")
conn.row_factory = sqlite3.Row

def initialize_db():
    conn = sqlite3.connect("UI.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS nodes(type, id PRIMARY KEY, timestamp DOUBLE)")
    c.execute("CREATE TABLE IF NOT EXISTS totals(type PRIMARY KEY, number)")
    c.execute("CREATE TRIGGER IF NOT EXISTS tally_upd AFTER UPDATE ON nodes BEGIN " + 
        "REPLACE INTO totals VALUES(new.type, (SELECT COUNT(*) FROM nodes WHERE type = new.type));" +
        "REPLACE INTO totals VALUES(old.type, (SELECT COUNT(*) FROM nodes WHERE type = old.type)); END;"
    )

    c.execute("CREATE TRIGGER IF NOT EXISTS tally_ins AFTER INSERT ON nodes BEGIN " + 
        "REPLACE INTO totals VALUES(new.type, (SELECT COUNT(*) FROM nodes WHERE type = new.type)); END;" +
        "REPLACE INTO totals VALUES(old.type, (SELECT COUNT(*) FROM nodes WHERE type = old.type)); END;"
    )

    c.execute("CREATE TRIGGER IF NOT EXISTS tally_del AFTER DELETE ON nodes BEGIN " + 
        "REPLACE INTO totals VALUES(old.type, (SELECT COUNT(*) FROM nodes WHERE type = old.type)); END;"
    )
    conn.commit()
    conn.close()


def send(message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        s.sendto(bytes(message, 'ascii'), (settings.COMMS_ADDR, settings.COMMS_PORT))


def handle(mess, addr, conn):

    c = conn.cursor()

    mess = json.loads(mess)
    if mess['action'] == "new_node":
            c.execute("REPLACE INTO nodes VALUES(?,?,?)", [mess['payload']['type'], mess['payload']['id']])


def database_log(data):
    c = conn.cursor()
    c.execute("REPLACE INTO nodes VALUES(?,?)", data)

def communicate_example(payload):

    #create a socket to communicate with the auth nodes
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

        #Create a hash of the node's public key to send to the auth node for identity verification
        keyhash = str(base64.b64encode(hashlib.sha256(rsa_encrypt.get_pub_key().exportKey("PEM")).digest()),'ascii')
        
        #Create an empty data and address variable and a socket to recieve the data
        data = ""
        addr = 0
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
        return addr

def send_clients():
    payload = ""
    
    c = conn.cursor()
    c.execute("SELECT * FROM totals")

    clients = c.fetchall()
    if clients == None:
        payload = json.dumps({"action":"err"})

    cliDict = {"action":"update_dbs"}
    cliDict["payload"] = []

    for i in clients:
        cliDict['payload'].append({"database":i['type'], "id":i['id']})

    payload = json.dumps(cliDict)

    send(payload)


def send_users():
    payload = ""
    
    c = conn.cursor()
    c.execute("SELECT * FROM shares")

    clients = c.fetchall()
    if clients == None:
        payload = json.dumps({"action":"err"})

    usrDict = {"action":"update_users"}
    usrDict["payload"] = []

    for i in clients:
        usrDict['payload'].append({"user":i['id'], "num_shares":i['num_shares']})

    payload = json.dumps(usrDict)

    send(payload)

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

        threading.Thread(target=handle, args=[mess, addr, conn]).start()
