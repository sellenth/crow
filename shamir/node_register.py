import socket
import sqlite3
import sys
import aes_crypt
import rsa_encrypt
import hashlib
import base64
import settings
import threading
import sqlite3
import shamir_updater

class Host():
    def __init__(self):
        self.host = "224.3.29.1"
        self.port = 13337

def register(host, s):
    payload = "imup:" + str(base64.b64encode(hashlib.sha256(rsa_encrypt.get_pub_key().exportKey("PEM")).digest()), 'ascii') + ":" + settings.ID
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s2:
        s2.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        s2.sendto(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), payload), ((host.host, host.port)))
    
    (cli, addr) = s.accept()
    
    arr = cli.recv(2048).split(b"::")
    sum1 = str(aes_crypt.aes_dec(rsa_encrypt.get_priv_key(), arr[0]), 'ascii')
    y = str(int(sum1) + 1)
    sum2 = str(aes_crypt.aes_dec(rsa_encrypt.get_priv_key_db(settings.ID), arr[1]), 'ascii')
    z = str(int(sum2) + 1)
    payload = aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), y  + ":" + z)
    cli.send(payload)
    
    conn = sqlite3.connect(settings.ID + ".db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS shares(id, x, y, key, timestamp)")
    c.execute("SELECT MAX(timestamp) from shares")
    timestamp = c.fetchone()[0]
    if timestamp == None:
        timestamp = 0
    cli.send(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), str(timestamp)))
    shamir_updater.update(rsa_encrypt.get_priv_key(), settings.ID)
    cli.close()
    return

def update(cli, address):
    data = cli.recv(2048)
    data = str(aes_crypt.aes_dec(rsa_encrypt.get_priv_key_db(settings.ID), data), 'ascii').split(":")
    if(data[0] == "keys"):
        print("keys")
    elif(data[0] == "user"):
        print("user")
    cli.close()

def startup():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 44432))
    s.listen(5)
    register(Host(), s)
    while 1 == 1:
        cli, address = s.accept()
        t = threading.Thread(update, args= [cli, address])
        t.start()

startup()