import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPV4, TCP 通訊協定
s.connect(('localhost', 5438))  # IP, PORT

while True:
    msg = input('請輸入訊息：')  # 讀取終端機的輸入訊息
    s.send(msg.encode('utf-8'))  # 轉成utf-8編碼再送出
    reply = s.recv(128)  # 接收伺服器的回應，最多128位元組

    if reply == b'quit':  # 回應若是quit則跳出
        print('關閉連線')
        s.close()
        break

    print(str(reply))  # 顯示回應內容
