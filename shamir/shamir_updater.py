import sqlite3
import sys
import socket
import aes_crypt
import rsa_encrypt
import base64

def update_db(data, conn):
    data = data.decode('utf-8').split(":")
    share = {}
    share['id'] = data[0]
    share['x'] = data[1]
    share['y'] = data[2]
    share['key'] = data[3]
    share['timestamp'] = data[4]
    c = conn.cursor()
    c.execute("SELECT * FROM shares WHERE id = ?", [share['id']])
    if(c.rowcount > 0):
        c.execute("UPDATE shares SET x = ?, y = ?, key = ?, timestamp = ?", [share["x"], share["y"], share["key"], share['timestamp']])
    else:
        c.execute("REPLACE INTO shares VALUES(?,?,?,?,?)", [share['id'], share['x'], share['y'], share['key'], share['timestamp']])
    conn.commit()

def update(key, db):
    conn = sqlite3.connect(db + ".db")
    conn.row_factory = sqlite3.Row
    conn.cursor().execute("CREATE TABLE IF NOT EXISTS shares(id, x, y, key, timestamp)")
    data = b""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 55588))
        s.listen(5)
        (cli, add) = s.accept()
        temp =""
        temp = cli.recv(4096)
        while not temp == "" and not len(temp) < 4096:
            data += temp
            temp = cli.recv(4096)
        data += temp
        cli.close()
    data = str(aes_crypt.aes_dec(key, data),'ascii').split(":")
    if data == ['']:
        return 
    for i in data:
        print(i)
        d = i.split("|")
        temp = rsa_encrypt.get_priv_key_db(db).decrypt((base64.b64decode(d[0]),)) + b':' + bytes(d[1], 'ascii')
        update_db(temp, conn)
    conn.close()