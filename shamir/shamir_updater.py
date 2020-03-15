import asyncore
import sqlite3
import sys

def update_db(data, conn):
    data = data.decode('utf-8').split(":")
    share = {}
    share['id'] = data[0]
    share['x'] = data[1]
    share['y'] = data[2]
    share['key'] = data[3]
    c = conn.cursor()
    c.execute("SELECT * FROM shares WHERE id = ?", share['id'])
    if(c.rowcount()):
        c.execute("UPDATE shares SET x = ?, y = ?, key = ?", share["x"], share["y"], share["key"])
    else:
        c.execute("INSERT INTO shares VALUES(?,?,?,?)", share['id'], share['x'], share['y'], share['key'])
    conn.commit()

class Shamir_Update_Handler(asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(4096)
        if data:
            update_db(data, conn)

class Shamir_Update_Server(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host,port))
        self.listen(5)
    
    def handle_accepted(self, sock, addr):
        Shamir_Update_Handler(sock)


conn = sqlite3.connect(sys.argv[1] + ".db")
conn.row_factory = sqlite3.Row
conn.cursor().execute("CREATE TABLE IF NOT EXISTS shares(id, x, y, key)")
server = Shamir_Update_Server('0.0.0.0',24448)
asyncore.loop()
