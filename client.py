import socket
import select
import errno
import sys
import random
import datetime

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

my_username = input("Username: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = my_username.encode("utf-8")
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)
date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log = open("Logs.txt", "a")
log.write(date_time + " Connection established with server for username " + my_username + "\n")
i = 'y'

while i != 'n':
	msg = open("message.txt", "r")
	all_lines = msg.readlines()
	date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print("Connection established - ACK")
	
	p = all_lines[random.randrange(0,13,1)]
	message = my_username + ">" + p
	print(message)
	log.write(date_time + " Message is " + p + "\n")
	i = input("Do you want to continue - y/n: ")
	if message:
		message = message.encode('utf-8')
		message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
		client_socket.send(message_header + message)

	try:
		while True:
			username_header  =client_socket.recv(HEADER_LENGTH)
			if not len(username_header):
				print("Connection closed by the server - NOACK")
				log.write(date_time + " Connection closed by the server \n")
				sys.exit()
			username_length = int(username_header.decode('utf-8').strip())
			username = client_socket.recv(username_length).decode('utf-8')

			message_header = client_socket.recv(HEADER_LENGTH)
			message_length = int(message_header.decode('utf-8').strip())
			message = client_socket.recv(message_length).decode('utf-8')
			print(f"{message}")

	except IOError as e:
		if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
			print('Reading error',str(e))
			log.write(date_time + " Reading error" + str(e) + "\n")
			sys.exit()
		continue

	except Exception as e:
		print("General error",str(e))
		log.write(date_time + " General error" + str(e) + "\n")
		sys.exit()

log.write(date_time + " Connection closed by " + my_username + "\n")