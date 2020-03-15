import shamir
import sqlite3

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

def add_shares(username, dbs, shares):
    if((not len(shares) == len(dbs))):
        #shares must be equal to dbs to prevent loss or oversharing
        return -1
    print(shares)
    for i in range(len(dbs)):
        conn = sqlite3.connect(dbs[i].name + ".db")
        c = conn.cursor()
        create = "CREATE TABLE IF NOT EXISTS shares(\"id\" PRIMARY KEY, \"x\", \"y\", \"key\")"
        print(create)
        c.execute(create)
        if(dbs[i].key):
            insert = "INSERT INTO shares VALUES(\"" + username +  "\",\"" + str(shares[i][0]) + "\",\""+ str(shares[i][1]) + "\", \"" + dbs[i].key+"\")"
            print(insert)
            c.execute(insert)
        else:
            insert = "INSERT INTO shares VALUES(\"" + username +  "\",\"" + str(shares[i][0]) + "\",\""+ str(shares[i][1]) + "\", NULL)"
            print(insert)
            c.execute(insert)
        conn.commit()
        conn.close()
def gen_secrets(username, name, dbs):
    if(len(dbs) < 4):
        exit(1)
    secret, shares = shamir.make_random_shares(3, len(dbs))
    add_secret(username, name, secret)
    add_shares(username, dbs, shares)

def add_user(username, name, db_list, keys):
    dbs = []
    for i in range(len(db_list)):
        dbs.append(db())
        dbs[i].name = db_list[i]
        dbs[i].key = keys[i]

    gen_secrets(username, name, dbs)

add_user("r3k", "Ryan Kennedy", ["web", "qr", "face", "voice"], ["","","",""])
add_user("tt", "Tom Tom", ["web", "qr", "face", "voice"], ["","","",""])