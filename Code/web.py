import socket

s = socket.socket()  # 預設IPV4, TCP 通訊協定
HOST = '0.0.0.0'  # 監聽所有連到控制器的IP
PORT = 80

httpHeader = b'''\
HTTP/1.0 200 OK

Welcome to MicroPython!
'''

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 設定socket參數，重複用地址
s.bind((HOST, PORT))  # IP, PORT
s.listen(5)  # 等待連線，最大可同時5個
print('{}伺服器在{}埠開通了'.format(HOST, PORT))

while True:
    client, addr = s.accept()  # 接收用戶連線，並傳回socket物件及IP位址
    print('用戶端位址：{}，埠號：{}'.format(addr[0], addr[1]))

    req = client.recv(1024)  # 接收伺服器的回應，最多1024位元組
    print('Request:')
    print(req)  # 顯示連線內容
    client.send(httpHeader)  # 傳送Http內容給用戶
    client.close()
    print('------------------')
