# Please make sure PyAudio and Python 3 are installed before run this Python file
# How to run: python3 voice.py

import speech_recognition as sr
import socket
import sys
import base64
import hashlib

r = sr.Recognizer()

text = ""

if __name__ == "__main__":
    if len(sys.argv) == 3:
        with sr.AudioFile(sys.argv[2]) as source:
            
            audio = r.record(source)

            try:
                text = r.recognize_google(audio)
                print(text)
            except:
                print('Sorry could not recognize your voice')
                exit(1)


        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 55556))

            voicehash = base64.b64encode(hashlib.sha256(bytes(text, 'ascii')).digest())

            s.send(voicehash)
    else:
        print('calling convention: command <username> <audiofile>')

