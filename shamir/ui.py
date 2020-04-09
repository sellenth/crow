#!/usr/bin/python3
import settings
import shamir_gen
import socket
import sqlite3
import time


#Delete all entries refering to a specefic id
def delete_all(id):
    
    #For each db in settigs
    for i in settings.DBS:

        #connect to that database, remove all shares with id == provided_id and commit the action
        conn = sqlite3.connect(i+".db")
        conn.cursor().execute("DELETE FROM enc_shares WHERE id = ?", [id])
        conn.commit()
        conn.close()


#Tell the auth server to send the designated user's share to the other auth nodes
def broadcast(uid):

    #Open a socket to the server
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', 55557))

            #send the username
            s.send(bytes(uid, 'ascii'))
    
    #Dont die if there is no auth server running
    except:
        return

#Recieves infomation from the user in order to add a user to the system or to delete one
def main():

    #Forever
    while 1 == 1:

        #Print the menu
        print("Register Or Update User\t(1)\n\nDelete User\t\t(2)\n\nExit\t\t\t(3)\n")

        #Grab the user's input
        choice = input()

        #To register a user
        if int(choice) == 1:
            
            #register user
            #cli_register()

            #Register user via client software
            net_register()

        #To delete user
        if int(choice) == 2:
            
            #delete user 
            delete()

        #Exit
        if int(choice) == 3:
            exit(0)


#Register a new user via cli
def cli_register():
    #Ask for and recieve uid
    print("Enter user id: ")
    uid = input().strip("\n")

    #Make sure the uid is less than 16 characters
    while len(uid) > 16:
        print("lets keep it under 16 chars")
        uid = input().strip("\n")

    #Ask for the user's name 
    print("Enter user's name: ")
    name = input().strip("\n")

    #Keep the name shorter than 16 characters
    while len(name) > 16:
        print("lets keep it under 16 chars")
        name = input().strip("\n")

    #Holder for user keys
    keys = []

    #For each db
    for i in settings.DBS:

        #Prompt for password
        print("Enter the user's password for the " + i + " database: ")
        temp = input().strip("\n")
        
        #Make sure the password isnt longer than a sha256 hash
        while len(temp) > 66:
            print("lets keep it under 66 chars")
            name = input().strip("\n")
        
        #append the key to the list
        keys.append(temp)

    #Send the gathered information to be entered into the proper databases
    shamir_gen.add_user(uid, name, keys)

    #Ask the auth server to share the new user
    broadcast(uid)


#Register a new user via network
def net_register():
    #Ask for and recieve uid
    print("Enter user id: ")
    uid = input().strip("\n")

    #Make sure the uid is less than 16 characters
    while len(uid) > 16:
        print("lets keep it under 16 chars")
        uid = input().strip("\n")

    #Ask for the user's name 
    print("Enter user's name: ")
    name = input().strip("\n")

    #Keep the name shorter than 16 characters
    while len(name) > 16:
        print("lets keep it under 16 chars")
        name = input().strip("\n")

    #Holder for user keys
    keys = []

    #Create a socket to get user passwords
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 55556))
        s.listen(5)

        #For each db
        for i in settings.DBS:

            #Prompt for password
            print("Send the user's password for the " + i + " database: ")
            
            #accept connection
            cli, addr = s.accept()

            #Get password
            temp = str(cli.recv(128), 'ascii').strip("\n")
            
            #Close connection
            cli.close()

            #Make sure the password isnt longer than a sha256 hash
            if len(temp) > 66:
                print("ERROR recieving pass, needs to be under 66 chars")
                return
            
            #append the key to the list
            keys.append(temp)

    #Send the gathered information to be entered into the proper databases
    shamir_gen.add_user(uid, name, keys)

    #Ask the auth server to share the new user
    broadcast(uid)


#Delete a user
def delete():
    #Ask for and recieve uid
    print("Enter user id: ")
    uid = input().strip("\n")

    #Connect to decrets databsae
    conn = sqlite3.connect("secrets.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    #Check if user exists
    c.execute("SELECT * FROM secrets where id = ?", [uid])
    s = c.fetchone()

    #If user doesnt exist than quit
    if s == None:
        conn.close()
        return
    
    #Mark the user as deleted
    c.execute("UPDATE secrets SET secret = \"DEL\", \"timestamp\" = ? WHERE id = ?", [time.time(), uid])

    #commit deletion
    conn.commit()
    conn.close()

    #Delete the remaining shares from the share databases
    delete_all(uid)

    #Broadcast the deletion
    broadcast(uid)


if __name__ == '__main__':
    main()