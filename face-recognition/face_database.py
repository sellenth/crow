import sqlite3 as sqlite
import json
import numpy as np

def init_db():
    conn = sqlite.connect('face.db')
    c = conn.cursor()
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS embeddings (
            id integer PRIMARY KEY AUTOINCREMENT,
            name text NOT NULL,
            embed text NOT NULL,
            num_faces integer NOT NULL
        )
        '''
    )
    conn.commit()
    return conn

def insert_db(name,embed,conn):
    c = conn.cursor()
    ins = (name,json.dumps([str(i) for i in list(embed)]))
    c.execute('INSERT INTO embeddings (name,embed,num_faces) VALUES(?,?,1)',ins)
    conn.commit()

def update_db(id,conn,name=None,embed=None,num=None):
    c = conn.cursor()
    if name is not None:
        params = (name,id)
        c.execute('UPDATE embeddings SET name=? WHERE id=?',params)
    if embed is not None:
        params = (embed,id)
        c.execute('UPDATE embeddings SET embed=? WHERE id=?',params)
    if num is not None:
        params = (num,id)
        c.execute('UPDATE embeddings SET num_faces=? WHERE id=?',params)
    conn.commit()

def search_db(id,conn):
    c = conn.cursor()
    n = (id,)
    for embed in c.execute('SELECT embed FROM embeddings WHERE id=?', n):
        try:
            embed = np.asarray(list(map(np.float,json.loads(embed[0]))))
            return embed
        except:
            print('ERROR: could not convert to list')
            return None

def getall_from_db(conn):
    c = conn.cursor()
    return [i for i in c.execute('SELECT * FROM embeddings')]

def delete_from_db(id,conn):
    c = conn.cursor()
    n = (id,)
    c.execute('DELETE FROM embeddings WHERE id=?',n)
    conn.commit()