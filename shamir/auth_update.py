import base64
import socket 
import aes_crypt
import rsa_encrypt
import settings
import hashlib
import sqlite3
from Crypto import Random
import time

class Host():
    def __init__(self):
        self.host = settings.MULT_ADDR
        self.port = settings.MULT_PORT

def delete_all(id):
    for i in settings.DBS:
        conn = sqlite3.connect(i+".db")
        conn.cursor().execute("REMOVE FROM shares WHERE id = ?", [id])
        conn.commit()
        conn.close()
    return

def fill_dbs(updates):
    for i in updates:
        conn = sqlite3.connect(i+".db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        shares = updates[i]
        print(i)
        if i == 'secrets':
            c.execute("CREATE TABLE IF NOT EXISTS secrets(\"id\" PRIMARY KEY, \"name\", \"secret\", \"timestamp\")")
            for j in shares:
                share = j.split("|")
                if(share[2] == "DEL"):
                    delete_all(share[0])
                c.execute("REPLACE INTO secrets VALUES (?, ?, ?, ?)", share)
        else:
            c.execute("CREATE TABLE IF NOT EXISTS enc_shares(\"id\" PRIMARY KEY, \"share\", \"timestamp\")")
            for j in shares:
                print(j)
                print(shares)
                share = j.split("|")
                print (share)
                c.execute("REPLACE INTO enc_shares VALUES(?, ?, ?)", share)
        conn.commit()
        conn.close()
    return

def grab_timestamp():
    conn = sqlite3.connect("secrets.db") 
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS secrets(\"id\" PRIMARY KEY, \"name\", \"secret\", \"timestamp\")")
    c.execute("SELECT MAX(timestamp) FROM secrets")
    timestamp = c.fetchone()[0]
    if timestamp == None:
        timestamp = 0
    conn.close()
    return str(timestamp)

def updateee():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 44441))
        s.listen(1)
        host = Host()
        payload = "woke:"
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s2:
            s2.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
            s2.sendto(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), "who?:"), ((host.host, host.port)))
            data = b""
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as us:
                try:  
                    us.bind(('0.0.0.0', 44443))
                    us.settimeout(.5)
                    data, address = us.recvfrom(128)
                except socket.timeout:
                    us.close()
                    return
            s2.sendto(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), "you!:" + str(data, 'ascii') + ":" + payload), ((host.host, host.port)))
        
        (cli, addr) = s.accept()
        data = cli.recv(1024)
        data = aes_crypt.aes_dec(rsa_encrypt.get_priv_key_auth(), data)
        data = str(data, 'ascii')
        data = str(int(data) + 1)
        cli.send(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), data + ":" + grab_timestamp()))
        data = b""
        temp = cli.recv(4096)
        while not temp == "" and not len(temp) < 4096:
            data += temp
            temp = cli.recv(4096)
        data += temp
        data = aes_crypt.aes_dec(rsa_encrypt.get_priv_key_auth(), data)
        data = str(data, 'ascii').split(":::")
        if time.time() - float(data[0]) > 15:
            return -1
        data = data[1:]
        for i in range(len(data)):
            data[i] = data[i].split("::")
        updates = {}
        for i in range(len(settings.DBS)):
            updates[settings.DBS[i]] = data[i]
        updates['secrets'] = data[-1]
        fill_dbs(updates)
    return

def updater(address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((address, 44441))
        challenge = int.from_bytes(Random.get_random_bytes(10), 'big')
        s.send(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), str(challenge)))
        response = s.recv(2048)
        response = str(aes_crypt.aes_dec(rsa_encrypt.get_priv_key_auth(), response), 'ascii').split(":")

        if (challenge + 1) == int(response[0], 0):
            timestamp = response[1]
            data = ""
            for i in settings.DBS:
                conn = sqlite3.connect(i + ".db")
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute("SELECT * FROM enc_shares WHERE timestamp > ?", [float(timestamp)])
                d = c.fetchall()
                for i in range(len(d)):
                    d[i] = d[i]["id"] + "|" + d[i]["share"] + "|" + str(d[i]["timestamp"])
                d = "::".join(d)
                data += (d + ":::")
                conn.close()
            conn = sqlite3.connect("secrets.db")
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM secrets WHERE timestamp > ?", [float(timestamp)])
            d = c.fetchall()
            for i in range(len(d)):
                d[i] = d[i]["id"] + "|" + d[i]["name"] + "|" + d[i]["secret"] + "|" + str(d[i]['timestamp'])
            print (d)
            data += "::".join(d)
            data = str(time.time()) + ":::" + data
            print(data)
            s.send(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), data))
            print("sent")
    return

