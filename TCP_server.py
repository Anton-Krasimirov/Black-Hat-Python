import socket
import threading

IP = '0.0.0.0'
PORT = 9998

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))# ip и port на които ще слуша сървъра
    server.listen(5)# не повече от 5 чакащи връзки
    print(f'[*] Lisening on {IP}:{PORT}')

    while True:
        client, address = server.accept()# когато клиентът се свърже получавам сокета му с данните
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(target=handle_client, args=(client,))

        client_handler.start()# създаваме нов поток, който сочи към нашата функция handle_client
        # и предаваме клиентската връзка към тази функция


def handle_client(client_socket):# Функцията handle_client извиква recv() и след това връща просто съобщение на клиента.
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')


if __name__ == '__main__':
    main()
