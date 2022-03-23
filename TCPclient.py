import socket
target_host = 'www.google.com'
target_port = 80

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# AF_INET = IPv4 , SOCK_STREAM = TCP

client.connect((target_host, target_port))# свързване

client.connect(b'GET / HTTP/1.1\r\nHost: google.com\r\n\r\n')# изпращане на данни като байтове

response = client.recv(4096)
print(response.decode())
client.close()