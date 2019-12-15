import socket
import ussl as ssl

url = 'https://micropython.org/ks/test.html'
_, _, host, path = url.split('/', 3)

addr = socket.getaddrinfo(host, 443)[0][-1]
s = socket.socket()
s.connect(addr)
s = ssl.wrap_socket(s)

httpHeader = b'''\
GET /{path} HTTP/1.1
Host: {host}
User-Agent: Mozilla/1.0

'''

s.write(httpHeader.format(path=path, host=host))

while True:
    data = s.read(128)
    if data:
        print(str(data, 'utf8'), end='')
    else:
        break
s.close()
