import shamir
import sqlite3
import rsa_encrypt
import time
import base64


class db:
    name = ""
    key = ""
    def __init__(self):
        self.name = ""
        self.key = ""

def add_secret(username, name, secret):
    conn = sqlite3.connect("secrets.db")

    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS secrets(\"id\" PRIMARY KEY, \"name\", \"secret\")")
    c.execute("INSERT INTO secrets VALUES (\"" + username +"\", \"" + name + "\", \"" + str(secret) + "\" )")
    conn.commit()
    conn.close()

def add_shares(username, dbs, shares, keys):
    if((not len(shares) == len(dbs))):
        #shares must be equal to dbs to prevent loss or oversharing
        return -1
    print(shares)
    for i in range(len(dbs)):
        conn = sqlite3.connect(dbs[i].name + ".db")
        c = conn.cursor()
        create = "CREATE TABLE IF NOT EXISTS enc_shares(\"share\" PRIMARY KEY, \"timestamp\")"
        c.execute(create)
        key = "NULL"
        if not dbs[i].key == "":
            key = dbs[i].key
        payload = username + ":" + str(shares[i][0])  + ":" + str(shares[i][1]) + ":" + str(key)
        k = ""
        for j in keys:
            if j.db == dbs[i].name:
                k = j
        payload = str(base64.b64encode(k.key.encrypt(bytes(payload, "ascii"), len(payload))[0]), "ascii")
        c.execute("INSERT INTO enc_shares VALUES(?, ?)", [payload, time.time()])
        conn.commit()
        conn.close()

def gen_secrets(username, name, dbs, keys):
    if(len(dbs) < 4):
        exit(1)
    secret, shares = shamir.make_random_shares(3, len(dbs))
    add_secret(username, name, secret)
    add_shares(username, dbs, shares, keys)

def add_user(username, name, db_list, keys_list):
    keys = rsa_encrypt.get_keys(db_list)
    dbs = []
    for i in range(len(db_list)):
        dbs.append(db())
        dbs[i].name = db_list[i]
        dbs[i].key = keys_list[i]
    
    gen_secrets(username, name, dbs, keys)

add_user("r3k", "Ryan Kennedy", ["web", "qr", "face", "voice"], ["","","",""])
add_user("tt", "Tom Tom", ["web", "qr", "face", "voice"], ["","","",""])