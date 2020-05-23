import settings
import socket
import struct
import threading
import json
import sqlite3

def initialize_db():
    conn = sqlite3.connect("UI.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS nodes(type, id PRIMARY KEY, timestamp DOUBLE)")
    c.execute("CREATE TABLE IF NOT EXISTS totals(type PRIMARY KEY, number)")
    c.execute("CREATE TRIGGER IF NOT EXISTS tally_upd AFTER UPDATE ON nodes BEGIN " + 
        "REPLACE INTO totals VALUES(new.type, (SELECT COUNT(*) FROM nodes WHERE type = new.type));" +
        "REPLACE INTO totals VALUES(old.type, (SELECT COUNT(*) FROM nodes WHERE type = old.type)); END;"
    )

    c.execute("CREATE TRIGGER IF NOT EXISTS tally_ins AFTER INSERT ON nodes BEGIN " + 
        "REPLACE INTO totals VALUES(new.type, (SELECT COUNT(*) FROM nodes WHERE type = new.type)); END;"
    )

    c.execute("CREATE TRIGGER IF NOT EXISTS tally_del AFTER DELETE ON nodes BEGIN " + 
        "REPLACE INTO totals VALUES(old.type, (SELECT COUNT(*) FROM nodes WHERE type = old.type)); END;"
    )
    conn.commit()


def send(message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        s.sendto(bytes(message, 'ascii'), (settings.COMMS_ADDR, settings.COMMS_PORT))

def handle(mess, addr, conn):

    c = conn.cursor()

    mess = json.loads(mess)
    if mess['action'] == "new_node":
            c.execute("REPLACE INTO nodes VALUES(?,?)", [mess['payload']['type'], mess['payload']['id']])

def run():

    initialize_db()

    address = settings.COMMS_ADDR
    port = settings.COMMS_PORT 
    tup = ('', port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(tup)
    group = socket.inet_aton(address)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    conn = sqlite3.connect("UI.db")
    conn.row_factory = sqlite3.Row

    while(1):
        mess, addr = s.recvfrom(4096)
        mess = str(mess, 'ascii')

        threading.Thread(target=handle, args=[mess, addr, conn]).start()