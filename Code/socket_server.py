import socket

HOST = 'localhost'
PORT = 5438
s = socket.socket()  # 預設IPV4, TCP 通訊協定
s.bind((HOST, PORT))  # IP, PORT
s.listen(1)  # 等待1個連線，最大可同時5個
print('{}伺服器在{}埠開通了'.format(HOST, PORT))
client, addr = s.accept()  # 接收用戶連線，並傳回socket物件及IP位址
print('用戶端位址：{}，埠號：{}'.format(addr[0], addr[1]))

while True:
    msg = client.recv(128).decode('utf-8')
    print('收到訊息：', msg)
    reply = ''

    if msg == '你好':
        reply = b'Hello!'
    elif msg == '再見':
        client.send(b'quit')
        break
    else:
        reply = b'what??'

    client.send(reply)

client.close()
