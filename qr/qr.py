from PIL import Image
import qrcode
import os
import sys
import hashlib
import base64
import socket

if __name__ == "__main__":
    if len(sys.argv) == 2:
        random = str(int.from_bytes(os.urandom(16), 'big'))

        img=qrcode.make(sys.argv[1] + ":" + random)
        img.save("out.png")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 55556))
            s.send(base64.b64encode(hashlib.sha256(bytes(random, 'ascii')).digest()))
    else:
        print("Use: command <user>")
