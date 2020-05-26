#!/usr/bin/python3
import settings
import shamir_gen
import socket
import sqlite3
import time
import sys

sys.path.append("../../face-recognition")
from face_register import *
from face_recog import *

#Delete all entries refering to a specefic id
def delete_all(uid):
    
    #For each db in settigs
    for i in settings.DBS:

        #connect to that database, remove all shares with id == provided_id and commit the action
        conn = sqlite3.connect(settings.DBdir + i+".db")

        #Create table if it doesnt exist
        conn.cursor().execute("CREATE TABLE IF NOT EXISTS enc_shares(id PRIMARY KEY, share, timestamp DOUBLE)")

        #Delete share and exit
        conn.cursor().execute("DELETE FROM enc_shares WHERE id = ?", [uid])
        conn.commit()
        conn.close()


#Tell the auth server to send the designated user's share to the other auth nodes
def broadcast(uid):

    #Open a socket to the server
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', 55558))

            #send the username
            s.send(bytes(uid, 'ascii'))
    
    #Dont die if there is no auth server running
    except:
        return

#Recieves infomation from the user in order to add a user to the system or to delete one
def main():

    #Forever
    while 1 == 1:

        #in case user presses letter instead of number
        try:
            #Print the menu
            print("Register/Update Via Tcp\t(1)\n")
            print("Register/Update Via Cli\t(2)\n")
            print("Delete User\t\t(3)\n")
            print("List Users\t\t(4)\n")
            print("Exit\t\t\t(5)\n")

            #Grab the user's input
            choice = input()

            #To register a user
            if int(choice) == 1:

                #Register user via client software
                net_register()

            if int(choice) == 2:
                
                #register user via cli
                cli_register()

            #To delete user
            if int(choice) == 3:
                
                #delete user 
                delete()

            #list users
            if int(choice) == 4:
                
                #list the users
                list_users()

            #Exit
            if int(choice) == 5:
                print("Thanks for using Crow!")
                return

            print("\n\n\nAction Completed!\n")
            time.sleep(1)
        #print error message and move on        

        except:
            print("oops, looks like there was an issue")


#lists all active users
def list_users():
    
    #Connect to decrets databsae
    conn = sqlite3.connect(settings.DBdir + "secrets.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    #Create the table if it doesnt exist
    c.execute("CREATE TABLE IF NOT EXISTS secrets(id PRIMARY KEY, name, secret, timestamp DOUBLE)")

    #Grab all undeleted users
    c.execute("SELECT id, name FROM secrets WHERE secret != ?", ["DEL"])
    users = c.fetchall()

    #Print all users to stdout and file
    #open file
    with open("../userlist.txt", 'w') as u:    
        print("Users:\n")
        u.write("Users:\n")
        for i in users:
            print("\tUser: " + i['id'] + "\n\tName: " + i['name'] +"\n" )
            u.write("\tUser: " + i['id'] + "\n\tName: " + i['name'] +"\n\n" )

    #wait until user is done 
    print("Users also saved in shamir/userlist.txt for your convience")
    print("Press Enter to continue")
    input()

    #close and exit
    conn.close()
    return

#Register a new user via cli
def cli_register():
    #Ask for and recieve uid
    print("Enter user id: ")
    uid = input().strip("\n").strip(":").strip("|")

    #Make sure the uid is less than 16 characters
    while len(uid) > 16:
        print("lets keep it under 16 chars")
        uid = input().strip("\n").strip(":").strip("|")

    #Ask for the user's name 
    print("Enter user's name: ")
    name = input().strip("\n").strip(":").strip("|")

    #Keep the name shorter than 16 characters
    while len(name) > 16:
        print("lets keep it under 16 chars")
        name = input().strip("\n").strip(":").strip("|")

    #Holder for user keys
    keys = []

    #For each db
    for i in settings.DBS:

        # register user's face
        if i is "face":
            print("Registering user's face")
            embed = register_face()
            if embed is None:
                # Handle error in registering face if needed
                pass
            tmp = embed_to_string(embed)
            keys.append(tmp)
        else:

            #Prompt for password
            print("Enter the user's password for the " + i + " database: ")
            temp = input().strip("\n").strip(":").strip("|")
            
            #Make sure the password isnt longer than a sha256 hash
            while len(temp) > 66:
                print("lets keep it under 66 chars")
                temp = input().strip("\n").strip(":").strip("|")
        
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
    uid = input().strip("\n").strip(":").strip("|")

    #Make sure the uid is less than 16 characters
    while len(uid) > 16:
        print("lets keep it under 16 chars")
        uid = input().strip("\n").strip(":").strip("|")

    #Ask for the user's name 
    print("Enter user's name: ")
    name = input().strip("\n").strip(":").strip("|")

    #Keep the name shorter than 16 characters
    while len(name) > 16:
        print("lets keep it under 16 chars")
        name = input().strip("\n").strip(":").strip("|")

    #Holder for user keys
    keys = []

    #Create a socket to get user passwords
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 55557))
        s.listen(5)

        #For each db
        for i in settings.DBS:

            #Prompt for password
            print("Send the user's password for the " + i + " database: ")
            
            #accept connection
            cli, addr = s.accept()

            #Get password
            temp = str(cli.recv(128), 'ascii').strip("\n").strip(":").strip("|")
            
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

    #Connect to secrets databsae
    conn = sqlite3.connect(settings.DBdir + "secrets.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    #Create the table if it doesnt exist
    c.execute("CREATE TABLE IF NOT EXISTS secrets(id PRIMARY KEY, name, secret, timestamp DOUBLE)")


    #Check if user exists
    c.execute("SELECT * FROM secrets where id = ?", [uid])
    s = c.fetchone()

    #If user doesnt exist than record deletion with unknown name
    if s == None:
        c.execute("INSERT INTO secrets VALUES(?,?,?,?)", [uid, "UNKNOWN", "DEL", time.time()])
        conn.commit()
        conn.close()


    else:
        #Mark the user as deleted
        c.execute("UPDATE secrets SET secret = ?, timestamp = ? WHERE id = ?", ["DEL", time.time(), uid])
        #commit deletion
        conn.commit()
        conn.close()

    #Delete the remaining shares from the share databases
    delete_all(uid)

    #Broadcast the deletion
    try:
        broadcast(uid)
        print("\nDeletion complete and broadcast to the auth nodes!")
        time.sleep(.5)
    
    #if unexpected error
    except:
        return 


#This just runs the main function
if __name__ == '__main__':

    #if not an auth node then exit
    if not settings.ID == 'auth':
        print("sorry this functionality is for auth nodes")
        exit(0)
    
    #runs main
    main()