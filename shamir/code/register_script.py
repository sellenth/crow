import shamir_gen
import ui
import sys
import socket
import settings

#register user via network
def net_register():

    #Holder for user keys
    keys = []

    #Create a socket to get user passwords
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind(('127.0.0.1', 55557))
        s.listen(5)

        #For each db
        for i in settings.DBS:
            
            #TODO SPAWN PROCESS in "node_programs.txt"

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
    shamir_gen.add_user(sys.argv[1], sys.argv[2], keys)

    #Ask the auth server to share the new user
    ui.broadcast(sys.argv[1])

if __name__ == "__main__":
    if len(sys.argv) == 3:
        net_register()
    else:
        print("usage: command <username> <name>\nThen Send 4 passwords via localhost:55556")