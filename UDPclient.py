import socket
target_host = '127.0.0.1'
target_port = 9997

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)# SOCK_DGRAM = UDP

client.sendto(b'AAAAAABBBBBBB', (target_port, target_port))# байнъри данни и сървира на който искаме да пратим
#  не ни е нужно connect()  преди взаимодействие UDP не поддържа връзки
data, addr = client.recvfrom(4096)# получаваме данни
print(data.decode())
client.close()