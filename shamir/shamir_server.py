import struct
import socket
import hashlib
import sqlite3
import time
import shamir_auth
import rsa_encrypt
import aes_crypt
import threading
import settings
import base64
import shamir_update_client
import auth_update
from Crypto import Random


#insert a blank user into the database to use as a baseline
def add_line(username, conn):
	c = conn.cursor()
	c.execute("INSERT INTO shares VALUES(\""+ username +"\",0,0,0,0,0,0,0,0)")
	conn.commit()


#authenticate a user based on a given id and share
#shares | id (PRIMARY KEY) | x1 | x2 | x3 | y1 | y2 | y3 | num_shares | timestamp
def auth_user(incoming, conn):
	
	#grab username and start db cursor
	username = incoming["id"]
	c = conn.cursor()

	#Grab already submitted shares
	c.execute("SELECT * FROM shares WHERE id = ?", [username])
	share = c.fetchone()
	
	if share == None:
		add_line(username, conn)
		c.execute("SELECT * FROM shares WHERE id = ?", [username])
		share = c.fetchone()

	#if the current time differs from the timestamp appended to the most recently added share (and conviently if no entry is present as timestamp will be 0)
	if time.time() - int(share["timestamp"]) > 60:
		
		#delete user entry
		c.execute("DELETE FROM shares WHERE id = \"" + username +"\"")
		
		#create blank user entry
		add_line(username, conn)

		#grab the share associated with the user
		c.execute("SELECT * FROM shares WHERE id = \""+ username +"\"")
		share = c.fetchone()

	#exit if 3 shares exist in the db (will be emptied after 60 seconds, prevents login spamming)	
	if share["num_shares"] >= 3:
		return

	#increment share counter
	i = share["num_shares"] +1
	
	#make sure we dont store duplicate shares
	for j in range(i):
		if share["x"+str(j+1)] == incoming["x"]:
			return
	
	#update the db with the new share, current time, and revised share count
	upd = "UPDATE shares SET x" + str(i)+" = ?, y" + str(i) + " = ?, num_shares = ?, timestamp = ? WHERE id = ?"
	c.execute(upd, [incoming['x'], incoming['y'], i, str(int(time.time())), username])
	conn.commit()


def add_secret(d):
	#open connection to shares database and set row generator and cursor
	conn = sqlite3.connect("shares.db")
	conn.row_factory = sqlite3.Row

	#make sure that shares table exists
	conn.cursor().execute("CREATE TABLE IF NOT EXISTS shares(id PRIMARY KEY, x1, y1, x2, y2, x3, y3, num_shares, timestamp FLOAT)")
	
	#create share object from provided data "d"
	share = {}
	share['id'] = d[0]
	share['x'] = d[1]
	share['y'] = d[2]

	#Add the share to the database if appropriate
	auth_user(share, conn)

	#pass execution to the authenticcator, which checks if the provided shares are valid
	shamir_auth.auth_user(share['id'], conn)


#this registers and updates a node at address
def register_node(data, address, keys, dbkeys):
	#Determine if the public key sent by the node is in the system
	for i in keys:
		if str(base64.b64encode(hashlib.sha256(i.key.exportKey("PEM")).digest()), 'ascii') == data[0]:
			#open connection to node for challenge-response authentication
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.connect((address[0], 44432))
				
				#pick 2 numbers, one for the db key, and one for the decvice key
				sum1 = str(int.from_bytes(Random.get_random_bytes(4), "big"))
				sum2 = str(int.from_bytes(Random.get_random_bytes(4), "big"))

				#encrypt the first number with device public key and the second with db public key
				pay = aes_crypt.aes_enc(i.key,sum1)
				pay2 = aes_crypt.aes_enc(dbkeys[data[1]].key,sum2)
				
				sum1 = int(sum1)
				sum2 = int(sum2)
				
				#send the two payloads
				s.send(pay + b'::'+ pay2)

				#recieve and check that valid data was recieved
				return_sums = str(aes_crypt.aes_dec(rsa_encrypt.get_priv_key_auth(), s.recv(2048)), 'ascii').split(":")
				if return_sums == -2 or return_sums == -1:
					return
				
				#convert the response to integer
				check1 = int(return_sums[0])
				check2 = int(return_sums[1])

				#validate that the node was able to read the data and modify it predictably
				if (sum1+1) == check1 and (sum2+1) == check2:
					#log that the node was registered and add its IP address and database to its associated key object
					i.ip = address[0]
					i.db = data[1]    
					
					#grab timestamp from node
					timestamp = str(aes_crypt.aes_dec(rsa_encrypt.get_priv_key_auth(), s.recv(1024)), 'ascii')
					#validate data and convert timstamp to float
					if timestamp == -1 or timestamp == -2:
						return
					
					timestamp = float(timestamp)
					
					#start node database update and print results when finished
					shamir_update_client.update(i, timestamp, s)
					print("Node registered:   " + data[1])
   

#this sends the servers associated number to the address specified
def contest(address, my_number, pub, keys):
	for i in keys:
		if i.hash == pub:
			with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
				data = aes_crypt.aes_enc(i.key, str(my_number)) 
				s.sendto(data, (address, 44443))


#this sends the servers associated number to the address specified
def contest_auth(address, my_number):
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		data = aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), str(my_number)) 
		s.sendto(data, (address, 44443))


#Handler for any multicast message that is recieved
def handle_response(data, address, my_number, keys, dbkeys):
	#Decrypt message and validate
	data = aes_crypt.aes_dec(rsa_encrypt.get_priv_key_auth(), data)
	print(data)
	#invalid data is ignored
	if data == -1 or data == -2:
		return

	#split the message and determine how to respond to it
	data = str(data, 'ascii').split(":")
	#Node is sending share for authentication
	if data[0] == "auth":
		threading.Thread(target=add_secret, args=[data[1:]]).start()
	
	#Node needs an auth node, so the auth contest is started using a node public key
	elif data[0] == "who?":
		threading.Thread(target = contest, args = [address[0], my_number, data[1], keys]).start()
	
	#An auth node has woken up, so the auth contest is started with the auth public key
	elif data[0] == "regA":
		threading.Thread(target = contest_auth, args = [address[0], my_number]).start()

	#Recieve an update when a user is registered or deleted
	elif data[0] == "here":
		threading.Thread(target = recv_update, args = [data[1]]).start()

	#A node has picked an auth node to use, check if it is this server
	elif data[0] == "you!":
		if int(data[1]) == my_number:
			#respond to startup update for client node
			if data[2] == "imup":
				threading.Thread(target=register_node, args=[data[3:], address, keys, dbkeys]).start()
			#respond to startup update for auth node
			elif data[2] == "woke":
				threading.Thread(target=auth_update.updater, args=[address[0]]).start()

def recv_update(data):
	data = data.split("||")
	if data[0] == rsa_encrypt.get_auth_hash():
		print(data)
		data = data[1:]
		print(data)
		for i in range(len(data)-1):
			if data[i] != '':
				conn = sqlite3.connect(settings.DBS[i] + ".db")
				conn.row_factory = sqlite3.Row
				c = conn.cursor()

				share = data[i].split("|")

				c.execute("REPLACE INTO enc_shares VALUES (?,?,?)", [share[0], share[1], share[2]])

				conn.commit()
				conn.close()


		conn = sqlite3.connect("secrets.db")
		conn.row_factory = sqlite3.Row
		c = conn.cursor()

		secret = data[-1].split("|")	

		if secret[2] == "DEL":
			auth_update.delete_all(secret[0])

		c.execute("REPLACE INTO enc_shares VALUES (?,?,?,?)", [secret[0], secret[1], secret[2], secret[3]])

		conn.commit()
		conn.close()
		print("Got share")

#Broadcasts a given user's shares adn secret to the auth nodes, 
#encrypted by the auth public key. It also sends a hash of the auth private key as identification
def broadcast(uid):
	shares = []
	
	for i in settings.DBS:
		conn = sqlite3.connect(i + ".db")
		conn.row_factory = sqlite3.Row
		c = conn.cursor()

		c.execute("SELECT * FROM enc_shares WHERE id = ?", [uid])
		shares.append(c.fetchone())
		conn.close()
	
	conn = sqlite3.connect("secrets.db")
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	
	c.execute("SELECT * FROM secrets WHERE id = ?", [uid])
	shares.append(c.fetchone())

	conn.close()

	data = ""
	for i in range(len(shares) -1):
		data += (str(shares[i]['id']) + "|" + str(shares[i]['share'] + "|" + str(shares[i]['timestamp'])) + "||")
	
	data += (str(shares[-1]['id']) + "|" + str(shares[-1]['name']) + "|" + str(shares[-1]['secret']) + "|" + str(shares[-1]['timestamp']))
	data = (rsa_encrypt.get_auth_hash() + "||" + data)

	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
		s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
		data = "here:" + data
		print(len(data))
		print(data)

		payload = aes_crypt.aes_enc(rsa_encrypt.get_pub_key_auth(), data)
		print(len(payload))
		s.sendto(payload, (settings.MULT_ADDR, settings.MULT_PORT))
	

#Start runs the shamir server, it is responsible for listening on the multicast
#address and assigning messages to the proper threads
def start():
	#set unique number -- not actually unicue but 1- (N* (1/2^16*8)) chance of being unique 
	my_number = int.from_bytes(Random.get_random_bytes(16), "big")
	
	#Grab database keys and device keys
	keys = rsa_encrypt.get_keys_nodes()
	dbkeys = rsa_encrypt.get_keys(settings.DBS)
	#Run the auth node update process which is required for the server to start properly
	auth_update.updateee() 
	
	#Set up multicast listener
	address = settings.MULT_ADDR
	port = settings.MULT_PORT 
	tup = ('', port)
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(tup)
	group = socket.inet_aton(address)
	mreq = struct.pack('4sL', group, socket.INADDR_ANY)
	s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	
	#Officialy start the server
	while 1 == 1:
		#grab data and sender from the ,ulticast address
		data, address = s.recvfrom(4096)
		#start response handler
		threading.Thread(target=handle_response, args=[data, address, my_number, keys, dbkeys]).start()



