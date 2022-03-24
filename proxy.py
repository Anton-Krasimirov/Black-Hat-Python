import sys
import socket
import threading


#  Създаваме HEXFILTER, низ с ASCII знаци за печат, ако знакът не може да се отпечата, вместо него се показва точка (.)
HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, lenght=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), lenght):
        word = str(src[i:i+lenght])
        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = lenght * 3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results


# hexdump('python rocks\n and proxies roll\n')


def receive_from(connection):
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer


def request_handler(buffer):
    # модифицируем пакет
    return buffer


def response_handler(buffer):
    # модифицируем пакет
    return buffer

'''Тази функция съдържа основната логика на нашия прокси сървър.  Първо се свързваме с отдалечения хост'''
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))# 1 свързваме с отдалечения хост

    if receive_first:# 2 След това се уверяваме, че не е необходимо да инициираме връзка с отдалечената страна и да изискваме данни, преди да влезем в главния цикъл
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)# 3
    '''Някои сървъри очакват клиентите да направят това (например, FTP сървърите обикновено първо изпращат приветствено съобщение).  
    След това функцията receive_from се използва и в двата края на връзката.  Той взема свързан обект на сокет и получава данните.  
    Съхраняваме съдържанието на пакета, за да можем по-късно да го анализираме в търсене на нещо интересно.  
    След това предаваме изхода на функцията response_handlerи изпращаме получения буфер на локалния клиент.'''
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>]Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")
        if not len(local_buffer) or not len(remote_buffer):# 4
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# 2
    try:
        server.bind((local_host, local_port))#2
    except Exception as e:
        print('problem on bind: %r' % e)
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)
    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:# 3
        client_socket, addr = server.accept()
        # отпечатай информация за локална връзка
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # създай нишка за взаимодействие с отдалечен сървър
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host,
            remote_port, receive_first))# 4
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == '__main__':
        main()