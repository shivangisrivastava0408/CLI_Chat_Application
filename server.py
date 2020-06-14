import socket
import select
import datetime
import random

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def multiplicative_inverse(a, m):
    a = a % m; 
    for x in range(1, m) : 
        if ((a * x) % m == 1) : 
            return x 
    return 1

def is_prime(num):
    if num == 2:
        return True
    if num < 2 or num % 2 == 0:
        return False
    for n in range(3, int(num**0.5)+2, 2):
        if num % n == 0:
            return False
    return True

def generate_keypair(p, q):
    n = p * q

    phi = (p-1) * (q-1)

    e = random.randrange(1, phi)

    g = gcd(e, phi)
    while g != 1:
        e = random.randrange(1, phi)
        g = gcd(e, phi)

    d = multiplicative_inverse(e, phi)
    
    return ((e, n), (d, n))

def encrypt(pk, plaintext):
    key, n = pk
    cipher = [(int(ord(char)) ** key) % n for char in plaintext]
    return cipher

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()

sockets_list = [server_socket]

clients = {}
date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log = open("Logs.txt", "a")
log.write(date_time + f'Listening for connections on {IP}:{PORT}... \n')
print(f'Listening for connections on {IP}:{PORT}...')

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())

        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False
list_of_clients = []
j = 21
while j > 0:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)

            clients[client_socket] = user
            cl_nm  = user['data'].decode("utf-8")
            if cl_nm not in list_of_clients:
                list_of_clients.append(cl_nm)
                j -= 1
            log.write(date_time + 'Accepted new connection from {}:{}, username: {} \n'.format(*client_address, user['data'].decode('utf-8')))
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        else:
            message = receive_message(notified_socket)

            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                log.write(date_time + 'Closed connection from: {} \n'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)

                del clients[notified_socket]
                break

            user = clients[notified_socket]
            p = 17
            q = 19
            public, private = generate_keypair(p, q)
            msg = message["data"].decode("utf-8")
            encrypted_msg = encrypt(private, msg)
            
            encrypted_msg = ''.join(map(lambda x: str(x), encrypted_msg))

            print(f'Received message in encrypted type from {user["data"].decode("utf-8")}: {encrypted_msg}')
            log.write(date_time + f' Received message in encrypted type from {user["data"].decode("utf-8")}: {encrypted_msg} \n')
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)

        del clients[notified_socket]