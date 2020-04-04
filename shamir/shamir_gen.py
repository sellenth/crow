import shamir
import sqlite3
import rsa_encrypt
import time
import base64
import settings


class db:
    name = ""
    key = ""
    def __init__(self):
        self.name = ""
        self.key = ""

def add_secret(username, name, secret, currtime):
    conn = sqlite3.connect("secrets.db")

    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS secrets(\"id\" PRIMARY KEY, \"name\", \"secret\", \"timestamp\")")
    c.execute("INSERT INTO secrets VALUES (?,?,?,?)", [username, name, str(secret), currtime])
    conn.commit()
    conn.close()

def add_shares(username, dbs, shares, keys, currtime):
    if((not len(shares) == len(dbs))):
        #shares must be equal to dbs to prevent loss or oversharing
        return -1
    for i in range(len(dbs)):
        conn = sqlite3.connect(dbs[i].name + ".db")
        c = conn.cursor()
        create = "CREATE TABLE IF NOT EXISTS enc_shares(\"id\" PRIMARY KEY, \"share\", \"timestamp\")"
        c.execute(create)
        key = "NULL"
        if not dbs[i].key == "":
            key = dbs[i].key
        payload = username + ":" + str(shares[i][0])  + ":" + str(shares[i][1]) + ":" + str(key)
        k = ""
        for j in keys:
            print(keys[j].db)
            print(dbs[i].name)
            if keys[j].db == dbs[i].name:
                k = keys[j]
        print (k)
        payload = str(base64.b64encode(k.key.encrypt(bytes(payload, "ascii"), len(payload))[0]), "ascii")
        c.execute("INSERT INTO enc_shares VALUES(?, ?, ?)", [username, payload, currtime])
        conn.commit()
        conn.close()

def gen_secrets(username, name, dbs, keys):
    if(len(dbs) < settings.TOTAL):
        exit(1)
    secret, shares = shamir.make_random_shares(settings.THRESH, len(dbs))
    currtime = time.time()
    add_secret(username, name, secret, currtime)
    add_shares(username, dbs, shares, keys, currtime)

def add_user(username, name, keys_list):
    keys = rsa_encrypt.get_keys(settings.DBS)
    dbs = []
    for i in range(len(settings.DBS)):
        dbs.append(db())
        dbs[i].name = settings.DBS[i]
        dbs[i].key = keys_list[i]
    
    gen_secrets(username, name, dbs, keys)

add_user("r3k", "Ryan Kennedy", ["","","",""])
add_user("tt", "Tom Tom",  ["","","",""])