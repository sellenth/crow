from random import choice
import string
import subprocess
import numpy
import zxing

#import qrcode

'''
with open('information.txt', 'w+') as f:
    user = []
    for line in f:
        user.append(list(line.strip('\n').split(',')
'''

user = {'a':123,'b':123,'c':123}

def newuser(name):
    #while True:
    #username = input('Enter the user_name:')
        if name in user.keys():
            print('username is already exist!')
        else:
        	pwd = input("please input your password:")
        	pwd2 = input("please confirm your password:")
        	if pwd != pwd2 or pwd == "" or pwd2 == "":
        		print("the number entered should be same!")
        	else:
        		with open('information.txt', 'w+') as f:
        			f.write(name+','+pwd+'\n')

        	#break
    #return username
            #subprocess.run("useradd %s &> /dev/null" % username, shell=True)
            #subprocess.run('echo %s | passwd --stdin %s &> /dev/null' % (pwd, username), shell=True)
            #break
        #return username


def olduser(username, password):
	with open('information.txt','r') as f:
		if int(password) == user[username]:
			print(username, "welcome back")
		else:
			print('there is no such person')


def login():
	N = 'New User Login'
	O = 'Old user Login'
	E = 'Exit'
	c = input('You are:New User Login or Old user Login or Exit?  N/O/E:)')
	if c == 'N':
		name = input('Please input your name:')
		newuser(name)
	elif c == 'O':
		username = input('name:')
		password = input('password:')
		olduser(username, password)
	else:
		print('Bye!')


def wfile(username,password,fname):
    with open(fname, 'information.txt') as f:
        data = username + '\t' + password + '\n'
        f.write(data)


'''
def make_code(text):
	qr = qrcode.QRCode(version=5,
 	error_correction=qrcode.constants.ERROR_CORRECT_L,
 	box_size=8,
 	border=4,
 	)
qr.add_data(text)
qr.make(fit = True)
img = qr.make_image()
img.show()
'''

if __name__ == '__main__':
    login()
