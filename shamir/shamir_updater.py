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
    c = conn.cursor()
    c.execute("SELECT * FROM shares WHERE id = ?", [share['id']])
    if(c.rowcount > 0):
        c.execute("UPDATE shares SET x = ?, y = ?, key = ?", [share["x"], share["y"], share["key"]])
        print("there")
    else:
        c.execute("INSERT INTO shares VALUES(?,?,?,?)", [share['id'], share['x'], share['y'], share['key']])
        print("here")
    conn.commit()

def update(key, port, db):
    conn = sqlite3.connect(db + ".db")
    conn.row_factory = sqlite3.Row
    conn.cursor().execute("CREATE TABLE IF NOT EXISTS shares(id, x, y, key)")
    data = ""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        s.listen(5)
        (cli, add) = s.accept()
        data = cli.recv(4096)
        cli.close()
    data = str(aes_crypt.aes_dec(key, data),'ascii').split(":")
    for i in data:
        temp = rsa_encrypt.get_priv_key_db(db).decrypt((base64.b64decode(i),))
        update_db(temp, conn)
    conn.close()


update(rsa_encrypt.get_priv_key(), 55558, "face")