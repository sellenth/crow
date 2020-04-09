#!/usr/bin/python3
import settings
import shamir_gen
import shamir_server
import socket

def broadcast(uid):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', 55557))

        s.send(bytes(uid, 'ascii'))


def main():
    while 1 == 1:
        menu = "Register Or Update User\t(1)\n\nDelete User\t\t(2)\n\nExit\t\t\t(3)\n"
        print(menu)
        choice = input()

        if int(choice) == 1:
            print("Enter user id: ")
            uid = input().strip("\n")
            while len(uid) > 16:
                print("lets keep it under 16 chars")
                uid = input().strip("\n")
            print("Enter user's name: ")
            name = input().strip("\n")
            while len(name) > 16:
                print("lets keep it under 16 chars")
                name = input().strip("\n")

            keys = []
            for i in settings.DBS:
                print("Enter the user's password for the " + i + " database: ")
                temp = input().strip("\n")
                while len(temp) > 66:
                    print("lets keep it under 66 chars")
                    name = input().strip("\n")
                keys.append(temp)

            shamir_gen.add_user(uid, name, keys)

            broadcast(uid)


        if int(choice) == 2:
            exit(2)
        if int(choice) == 3:
            exit(0)

if __name__ == '__main__':
    main()