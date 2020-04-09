# crow

# Shamir

To use the shamir software some set up is required. It is a bit lengthy and manual, but this is to prevent private keys being leaked, and unauthorized public keys from being added to the node list.

All directories refrenced are from the context of crow/shamir

1: Log in to an auth node and cd to 'crow/shamir', change the settings file to match your set up. An example file is provided below.

```
#Global settings cariables for easy management

#List of the databases you are using
DBS = ["face", "qr", "voice", "web"]

#The identity of this node, should be auth or one of the database names
ID = 'auth'

#The total number of nodes in this system
TOTAL = 4

#The number of shares that need to be sent to authenticate a user successfully
#Changeing this number will break an active system. After changing you must regenerate shares for all users.
THRESH = 3

#The multicast address and port to use for this system. Do not change unless you need to
MULT_ADDR = '224.3.29.1'
MULT_PORT = 13337
```

2: Create dataabase and auth keys. Run the rsa_encrypt.py program and select the generate_db_keys option, then run it again and select the auth_key option.

3: Copy the database and all keys to a flash drive from the 'assets' directory, leave only the .pub keys and the 'auth' file, this is the auth private key. If you plan to convert your auth node to a database node later also create a local key with rsa_encrypt.

4: For each node update the settings file as appropriate and copy the following files to the assets directory.

  Auth Nodes: all database .pub files and the file 'auth'
  Client Nodes: The private and public key matching their database ex. 'face' and 'face.pub' and the auth public key 'auth.pub'
  
  For client nodes run rsa_encrypt and generate a local key. Copy the file "$(long_number)".pub to the flash drive in a seperate      folder

5: For each auth node copy the folder with the local public keys into the directory assets/hosts

6: Done! You cannow run ./crow_caw to start the server on each device. Feel free to set this up as a recurring job. To add test users use ./shamir_gen.py and to add real users use ./ui.py I will explain how to do this below

## Creating Users
