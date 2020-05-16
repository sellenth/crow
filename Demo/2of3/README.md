To initialize this demo do the following

    Install npm, docker, and docker-compose.
    
    Navigate to the crow/ui directory and run "npm run build"
    
    run docker-compose up -d --build

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
