# crow

# Code Review Feedback

| Category | Feedback | Response |
| -------- | -------- | -------- |
| Build | Project is very messy to build and there are two entirely different sections that require building. The containerization is a great initiative but we need to work on tieing it all together. Having one command to build the project should be priority number one. | The build has been reworked into one unified 2of3 demo. All users have to do is run a single script in the project's home directory and the whole project will be built and demo containers will be created on static IPs. The web servers running on these containers will then be automatically launched in the user's default browser. |
| Legibility | The python backend is documented generously and helps step a developer through all of what is happening.  There is an attempt to comment the dashboard view and the underlying node server but it is fairly cluttered and would not be easy to pick back up in 6 months. | The web server and React code has been reworked and recomomented. It should be easier to approach now for someone new to the project or someone picking up the project after a long break. |
| Implementation | There is a visible attempt at abstraction for different UI views. They are all called from the same root component and switch upon a singular change in the settings file. The python files are ordered in a sane fashion where an external function can be roughly understood by its name and context alone. | More features have been added to the program since the review. The QR page has been constructed to scan the webcam for QR codes in realtime and also generate a QR code for the user upon registration. The Voice authentication page has also been added. Additionally, users can now register from the dashboard view and the dashboard persists its state through page changes. |
| Maintainability | Tangentially related to the build clutter, the project is not in a state now where it is easily maintainable by members of the group, let alone a fresh pair of eyes. We need to streamline our README and clean up the node server and react structure or at least provide some high level documentation within those files. | New comments added to the code make it much easier to understand. The design for the web experience is admittedly still not logical and could use a major refactor. |
| Design Requirements | All of the requirements listed under “current progress” are essentially done, there is just the data pipeline and example nodes to implement to bring the project together. The document does a good job of demonstrating what is and is not completed. | All the remaining requirements that were "current progress" are now done. Client has reviewed our project and verified that it satisfies their requirements. |
| Other | Get the build reliably working with as little fiddling as possible. If we can have the project build then we have enough to demonstrate what the vision is and that should be good enough for the expo. | The demo build is in a much better place now. |


# Demonstration

A demonstration of two systems is included in the Demo directory. This demonstration shows a 2 out of 5 authentication scheme and a 3 out of 4 authentication scheme. Instructions on how to start and interact with the demo are within the Demo folder.

The demo runs using docker-compose so please install Docker and Docker-compose if you intend on  running the demo. The docker containers represnet the small systems this software was designed to run on, and allow easy deployment of many nodes. 

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
