import socket
import sqlite3
import sys
import aes_crypt
import rsa_encrypt
import hashlib
import base64

class Host():
    def __init__(self):
        self.host = "224.3.29.1"
        self.port = 13337

def register(host):
    payload = "imup:" + str(base64.b64encode(hashlib.sha256(rsa_encrypt.get_pub_key().exportKey("PEM")).digest()), 'ascii')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        s.sendto(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), payload), ((host.host, host.port)))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 44432))
        s.listen(1)
        s.accept()
        x = aes_crypt.aes_dec(rsa_decrypt.get_priv_key(), s.recv(256))
        y = str(int(str(x, 'ascii')) + 1)
        s.send(aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), y))
        
    
    return

register(Host())