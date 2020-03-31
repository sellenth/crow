import struct
import socket
import hashlib
import sqlite3
import time
import shamir_auth
import rsa_encrypt
import aes_crypt
import threading
import base64
from Crypto import Random

def add_line(username, conn):
    c = conn.cursor()
    c.execute("INSERT INTO shares VALUES(\""+ username +"\",0,0,0,0,0,0,0,0)")
    conn.commit()

def auth_user(incoming, conn):
    print(str(incoming))
    username = incoming["id"]
    c = conn.cursor()

    c.execute("SELECT * FROM shares WHERE id = \""+ username +"\"")
    share = c.fetchall()
    if not len(share) == 1: 
        add_line(username, conn)
        c.execute("SELECT * FROM shares WHERE id = \""+ username +"\"")
        share = c.fetchall()

    if time.time() - int(share[0]["timeout"]) > 60:
        c.execute("DELETE FROM shares WHERE id = \"" + username +"\"")
        add_line(username, conn)
        c.execute("SELECT * FROM shares WHERE id = \""+ username +"\"")
        share = c.fetchall()
    share = share[0]
    
    
    if share["num_shares"] >= 3:
        return
    i = share["num_shares"] +1
    for j in range(i):
        if share["x"+str(j+1)] == incoming["x"]:
            return
    upd = "UPDATE shares SET x" + str(i)+" = \"" +incoming["x"]+ "\", y" + str(i) + " = \"" + incoming["y"] + "\", num_shares = " + str(i) +", timeout = " + str(int(time.time())) + " WHERE id = \"" + username + "\""
    c.execute(upd)
    conn.commit()

def add_secret(d):
    conn = sqlite3.connect("shares.db")
    conn.row_factory = sqlite3.Row
    conn.cursor().execute("CREATE TABLE IF NOT EXISTS shares(id, x1, y1, x2, y2, x3, y3, num_shares, timeout)")
    d = d.decode("utf-8").split(":")
    share = {}
    share['id'] = d[0]
    share['x'] = d[1]
    share['y'] = d[2]
    auth_user(share, conn)
    shamir_auth.auth_user(share['id'], conn)

def register_node(data, address, keys):
    data = str(data, 'ascii').split(":")
    print(data)

    for i in keys:
        if str(base64.b64encode(hashlib.sha256(i.key.exportKey("PEM")).digest()), 'ascii') == data [0]:
            print(address)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((address[0], 44432))
                x = str(int.from_bytes(Random.get_random_bytes(4), "big"))
                s.send(aes_crypt.aes_enc(i.key,x))
                y = str(aes_crypt.aes_dec(rsa_encrypt.get_priv_key_auth(), s.recv(256)), 'ascii')
                x = int(x)
                y = int(y)
                if (x+1) == y:
                    i.ip = address[0]
                    print("WWWWWWOOOOOOOOOOTTTTT")
            break

def Shamir_Server_Multicast(address, port):
    tup = ('', port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(tup)
    group = socket.inet_aton(address)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    keys = rsa_encrypt.get_keys_nodes()
    while 1 == 1:
        data, address = s.recvfrom(1024)
        data = aes_crypt.aes_dec(rsa_encrypt.get_priv_key_auth(), data)
        if data[0:5] == b"auth:":
            t = threading.Thread(target=add_secret, args=[data[5:]])
            t.start()
        elif data[0:5] == b"imup:":
            t = threading.Thread(target=register_node, args=[data[5:], address, keys])
            t.start()
        else:
            continue


Shamir_Server_Multicast('224.3.29.1',13337)
