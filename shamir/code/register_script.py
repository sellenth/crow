import sys
import rsa_encrypt
import aes_crypt
import comms
import settings
import socket

#register user via network
def register(user, name, keys):
    payload = "usrW" + ":" + rsa_encrypt.get_auth_hash() + ":" + user + ":" + name + ":" + ":".join(keys)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

        payload = aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), payload)
        s.sendto(payload, (settings.MULT_ADDR, settings.MULT_PORT))


if __name__ == "__main__":
    register(sys.argv[1], sys.argv[2], sys.argv[3:])