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

my_number = int.from_bytes(Random.get_random_bytes(16), "big")
#Grab database keys and device keys
keys = rsa_encrypt.get_keys_nodes()
dbkeys = rsa_encrypt.get_keys(settings.DBS)

#insert a blank user into the database to use as a baseline
def add_line(username, conn):
	c = conn.cursor()
	c.execute("INSERT INTO shares VALUES(\""+ username +"\",0,0,0,0,0,0,0,0)")
	conn.commit()

#authenticate a user based on a given id and share
def auth_user(incoming, conn):
	
	#grab username and start db cursor
	username = incoming["id"]
	c = conn.cursor()

	#Grab already submitted shares
	c.execute("SELECT * FROM shares WHERE id = \""+ username +"\"")
	share = c.fetchall()

	#if there are no
	if not len(share) == 1:
		print("hello") 
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
	upd = "UPDATE shares SET x" + str(i)+" = ?, y" + str(i) + " = ?, num_shares = ?, timeout = ? WHERE id = ?"
	c.execute(upd, [incoming['x'], incoming[y], i, str(int(time.time())), username])
	conn.commit()

def add_secret(d):
	conn = sqlite3.connect("shares.db")
	conn.row_factory = sqlite3.Row
	conn.cursor().execute("CREATE TABLE IF NOT EXISTS shares(id, x1, y1, x2, y2, x3, y3, num_shares, timeout)")
	share = {}
	share['id'] = d[0]
	share['x'] = d[1]
	share['y'] = d[2]
	auth_user(share, conn)
	shamir_auth.auth_user(share['id'], conn)

#this registers and updates a node at address
def register_node(data, address):
	#Determine if the public key sent by the node is in the system
	for i in keys:
		if str(base64.b64encode(hashlib.sha256(i.key.exportKey("PEM")).digest()), 'ascii') == data [0]:
			#open connection to node for challenge-response authentication
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.connect((address[0], 44432))
				
				#pick 2 numbers, one for the db key, and one for the decvice key
				sum1 = str(int.from_bytes(Random.get_random_bytes(4), "big"))
				sum2 = str(int.from_bytes(Random.get_random_bytes(4), "big"))
				sum1 = int(sum1)
				sum2 = int(sum2)

				#encrypt the first number with device public key and the second with db public key
				pay = aes_crypt.aes_enc(i.key,sum1)
				pay2 = aes_crypt.aes_enc(dbkeys[data[1]].key,sum2)
				
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
					
					#start node database update
					shamir_update_client.update(i.key, timestamp, shamir_update_client.Host(address[0]), i.db)


#this sends the servers associated number to the address specified
def contest(address):
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		for i in keys:
			if i.ip == address:
				s.sendto(aes_crypt.aes_enc(i.key, str(my_number)), (address, 44443))
				return

def handle_response(data, address)
	#Decrypt message and validate
	data = aes_crypt.aes_dec(rsa_encrypt.get_priv_key_auth(), data)
	
	#invalid data is ignored
	if data == -1 or data == -2:
		continue

	#split the message and determine how to respond to it
	data = str(data, 'ascii').split(":")

	#Node is sending share for authentication
	if data[0] == "auth":
		threading.Thread(target=add_secret, args=[data[1:]]).start()
	
	#Node needs an auth node, so the auth contest is started
	elif data[0] == "who?":
		threading.Thread(target = contest, args = [my_number, address[0]]).start()
	
	#A node has picked an auth node to use, check if it is this server
	elif data[0] == "you!":
		if int(data[1]) == my_number:
			#respond to startup update for client node
			if data[2] == "imup":
				threading.Thread(target=register_node, args=[data[3:], address]).start()
			#respond to startup update for auth node
			elif data[2] == "woke":
				threading.Thread(target=auth_update.updater, args=[address[0]]).start()


#Start runs the shamir server, it is responsible for listening on the multicast
#address and assigning messages to the proper threads
def start():
	#Run the auth node update process which is required for the server to start properly
	auth_update.updateee()

	#Set id number for auth contest  
	
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
		threading.Thread(target=handle_response, args=[data, address]).Start()



