import asyncore
import sqlite3
import time
import shamir_auth

def add_line(username, conn):
    c = conn.cursor()
    c.execute("INSERT INTO shares VALUES(\""+ username +"\",0,0,0,0,0,0,0,0)")
    conn.commit()

def auth_user(incoming, conn):
    print(str(incoming))
    username = incoming["id"]
    c = conn.cursor()

    c.execute("SELECT * FROM shares WHERE id = \""+ username +"\"")
    share = c.fetchall()
    if not len(share) == 1: 
        add_line(username, conn)
        c.execute("SELECT * FROM shares WHERE id = \""+ username +"\"")
        share = c.fetchall()

    if time.time() - int(share[0]["timeout"]) > 60:
        c.execute("DELETE FROM shares WHERE id = \"" + username +"\"")
        add_line(username, conn)
        c.execute("SELECT * FROM shares WHERE id = \""+ username +"\"")
        share = c.fetchall()
    share = share[0]
    
    
    if share["num_shares"] >= 3:
        return
    i = share["num_shares"] +1
    for j in range(i):
        if share["x"+str(j+1)] == incoming["x"]:
            return
    upd = "UPDATE shares SET x" + str(i)+" = \"" +incoming["x"]+ "\", y" + str(i) + " = \"" + incoming["y"] + "\", num_shares = " + str(i) +", timeout = " + str(int(time.time())) + " WHERE id = \"" + username + "\""
    c.execute(upd)
    conn.commit()

def add_secret(d, conn):
    d = d.decode("utf-8").split(":")
    share = {}
    share['id'] = d[0]
    share['x'] = d[1]
    share['y'] = d[2]
    auth_user(share, conn)
    shamir_auth.auth_user(share['id'], conn)


class Shamir_Handler(asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(4096)
        if data:
            add_secret(data, conn)

class Shamir_Server(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host,port))
        self.listen(5)
    
    def handle_accepted(self, sock, addr):
        Shamir_Handler(sock)

conn = sqlite3.connect("shares.db")
conn.row_factory = sqlite3.Row
conn.cursor().execute("CREATE TABLE IF NOT EXISTS shares(id, x1, y1, x2, y2, x3, y3, num_shares, timeout)")
server = Shamir_Server('0.0.0.0',13337)
asyncore.loop()
