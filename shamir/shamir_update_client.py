import socket
import sqlite3
import sys
import aes_crypt
import rsa_encrypt

class Host():
    def __init__(self, ip, port):
        self.host = ip
        self.port = port

def send_share(key, shares, host):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host.host, host.port))    
        payload = aes_crypt.aes_enc(key, ':'.join(shares))
        s.send(payload)
        return

def grab(t, n): 
    conn = sqlite3.connect(n + ".db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM enc_shares WHERE timestamp > ?", [float(t)])
    temp = c.fetchall()
    shares = []
    for i in temp:
        shares.append(i['share'])
    conn.close()
    return shares

def update(key, t, host, db):
    shares = grab(t, db)
    send_share(key, shares, host)
    return 1

key = rsa_encrypt.get_pub_key()
update(key, 0, Host("192.168.1.223", 55558), "face")

