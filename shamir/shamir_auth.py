import shamir
import sqlite3
import time

def auth_user(username, conn):
    c = conn.cursor()

    c.execute("SELECT * FROM shares WHERE id = \""+ username +"\"")
    share = c.fetchall()
    if not len(share) == 1: 
        print(c.rowcount)
        raise Exception("User does not exist")
    share = share[0]
    return validate(share)

def validate(share):
    if time.time() - int(share["timeout"]) > 60:
        print("No auth for you, timeout!")
        return
    if not share["num_shares"] == 3:
        print(share["id"] + " has submitted " + str(share["num_shares"]) + " shares!")
        return
    s = []
    s.append((int(share["x1"]), int(share["y1"])))
    s.append((int(share["x2"]), int(share["y2"])))
    s.append((int(share["x3"]), int(share["y3"])))
    secret = shamir.recover_secret(s)
    conn = sqlite3.connect("secrets.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM secrets WHERE id = \""+ share["id"] +"\"")
    res = c.fetchone()
    if res["secret"] == str(secret):
        print(res["name"] + " is Authorized!")
    else:
        print("No auth for you!")
    return
