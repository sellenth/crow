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
import time
import shamir_client

class Host():
    def __init__(self):
        self.host = settings.MULT_ADDR
        self.port = settings.MULT_PORT


def challenge(payload):
    print("challenging")
    host = Host()
    k = str(base64.b64encode(hashlib.sha256(rsa_encrypt.get_pub_key().exportKey("PEM")).digest()), 'ascii')
    print(k)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        s.sendto(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), "who?:" + k), ((host.host, host.port)))
        data = ""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as us:
            us.bind(('0.0.0.0', 44443))
            data, address = us.recvfrom(4096)
        data = aes_crypt.aes_dec(rsa_encrypt.get_priv_key(), data)
        data = str(data, 'ascii')
        s.sendto(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), "you!:" + data + ":" + payload), ((host.host, host.port)))

def register(host, s):
    keyhash = str(base64.b64encode(hashlib.sha256(rsa_encrypt.get_pub_key().exportKey("PEM")).digest()),'ascii')
    payload = "imup:" + keyhash + ":" + settings.ID
    challenge(payload)
      
    (cli, addr) = s.accept()
    
    check = cli.recv(2048)
    
    sums = str(aes_crypt.aes_dec(rsa_encrypt.get_priv_key_db(settings.ID), check), 'ascii')
    sum1 = str(int(sums[0]) + 1)
    sum2 = str(int(sums[1]) + 1)
    payload = aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), sum1 + ":" + sum2)
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
    if(data[0] == "user"):
        print("user")
    cli.close()
    return

def timer_update_start():
    return

def start():
    print("started")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 44432))
    s.listen(5)
    register(Host(), s)
    threading.Thread(shamir_client.start()).start()
    threading.Thread(timer_update_start()).start()
    while 1 == 1:
        cli, address = s.accept()
        t = threading.Thread(update, args= [cli, address])
        t.start()