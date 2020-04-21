# crow

# Demonstration

A demonstration of two systems is included in the Demo directory. This demonstration shows a 2 out of 5 authentication scheme and a 3 out of 4 authentication scheme. Instructions on how to start and interact with the demo are within the Demo folder.

The demo runs using docker-compose so please install Docker and Docker-compose if you intend on  running the demo. The docker containers represnet the small systems this software was designed to run on, and allow easy deployment of many nodes. 

# UI Demonstration
In order to see what the system dashboard will look like, follow these steps
1. Copy/paste into terminal: `git clone https://github.com/sellenth/crow.git; cd crow/ui; npm install; npm run-script build; cd ..; cd express; npm install; npm start &`
1. access the webpage at localhost:3001
1. pull up a terminal so that both the browser and terminal are visible 
1. run the /shamir/code/demo_output.sh script, it will submit strings to the server upon the press of any key

# Shamir Setup

To use the shamir software some set up is required. It is a bit lengthy and manual, but this is to prevent private keys being leaked, and unauthorized public keys from being added to the node list.

All directories refrenced are from the context of crow/shamir

1. Log in to an auth node and cd to 'crow/shamir', change the settings file to match your set up. An example file is provided below.

```
#Global settings cariables for easy management

#List of the databases you are using
DBS = ["face", "qr", "voice", "web"]

#The identity of this node, should be auth or one of the database names
ID = 'auth'

#The total number of nodes in this system
TOTAL = 4

#The number of shares that need to be sent to authenticate a user successfully
#Changing this number will break an active system. After changing you must regenerate shares for all users.
THRESH = 3

#The multicast address and port to use for this system. Do not change unless you need to
MULT_ADDR = '224.3.29.1'
MULT_PORT = 13337
```

2. Create database and auth keys. Run the rsa_encrypt.py program and select the generate_db_keys option, then run it again and select the auth_key option.

3. Copy the database and all keys to a flash drive from the 'assets' directory, leave only the .pub keys and the 'auth' file, this is the auth private key. If you plan to convert your auth node to a database node later also create a local key with rsa_encrypt.

4. For each node update the settings file as appropriate and copy the following files to the assets directory.

  Auth Nodes: all database .pub files and the file 'auth'
  Client Nodes: The private and public key matching their database ex. 'face' and 'face.pub' and the auth public key 'auth.pub'
  
  For client nodes run rsa_encrypt and generate a local key. Copy the file "$(long_number)".pub to the flash drive in a seperate      folder
  
5. For each auth node copy the folder with the local public keys into the directory assets/hosts

6. Done! You cannow run ./crow_caw to start the server on each device. Feel free to set this up as a recurring job. To add test users use ./shamir_gen.py and to add and delete real users use ./ui.py I will explain how to do this below

# Creating Users

Creating users can only be done on an auth node

To create users using the ./ui.py program you can use the cli to enter data and you can use the node software or the cli to input passwords. 

To use node software simply set up your program to read user data, if this produces data longer then 66 characters. Or it is in a non-string format, or should be obfuscated then sumbit a base64 encoded sha256 hash.

To submit a password open a TCP socket to ('127.0.0.1', 55556) and s.send() the password

To register a user you will need to do this with the software you are using for each database. In the default case this means registering the user's face, qr code, voice command, and pin.

After submitting the information the user's information will be registered and broadcast to all active auth nodes. Within the next 3.5 minutes (the client node update interval) the user will be able to log in succesfully.

# Authenticating users

To authenticate a user from a client node simply open a tcp socket to ('127.0.0.1', 55556) and send the user's information in the format user:password, or you can run the "submit.py" script. The client node will handle the rest and sent the user's share to the auth nodes if the information presented is correct.
