To initialize this demo do the following


    Install Docker and docker-compose
    
    run docker-compose up -d
    There are now 4 containers running on ports 

        auth1: 44444
        web: 44441
        qr: 44442
        voice: 44443
    
    Ssh into each of these containers and run "./demo_init.py"

        "ssh root@localhost -p 4444*"

        The password is "crow"

    Now the system is initialized

    You can now start the service on all machines by navigating to "crow/express" and running "npm start"
    
    The nodes will now have webservers running on the following addresses.
        
        https://172.28.1.1:3001
        https://172.28.1.2:3001
        https://172.28.1.3:3001
        https://172.28.1.4:3001
        
   Enjoy!
   
    To create initial users run "./shamir_gen" on an auth node
    To create more users run "./ui.py"

    You can now start the service on all machines by using tmux and/or "./crow_caw.py &"
    
    Tmux is very helpful in this situation as you can run ./crow_caw.py in tmux then exit it (ctrl+b, d) and run "./ui.py" or "./submit.py"

    To enter a share on a client node run the "./submit.py" script while crow_caw is running which will prompt you for a username and password

    Notes:
        To add users via network run "nc localhost 55556" to feed passwords to the script
        But the cli is much easier for this demo

        Each node can have a seperate password, and any 3 of them will succesfully authenticate a user

        Be warned, after entering a new user, it can take up to 3.5 minutes by design for the client nodes to recieve this update.
        The client nodes ask for updates on this regular interval so as to not interrupt the system.
