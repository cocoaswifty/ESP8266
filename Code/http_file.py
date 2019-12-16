# -*- coding: utf-8 -*-

import socket
import os
import gc

HOST = '0.0.0.0'
PORT = 80
WWWROOT = '/www/'

httpHeader = '''HTTP/1.0 200 OK
Content-type: {}
Content-length: {}

'''

mimeTypes = {
    '.txt': 'text/plain',
    '.htm': 'text/html',
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.xml': 'application/xml',
    '.json': 'application/json',
    '.jpg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
}


def checkFileSize(path):
    try:
        s = os.stat(path)  # 取得檔案資訊

        if s[0] != 16384:  # 確認不是資料夾
            fileSize = s[6]  # 取得檔案大小
        else:
            fileSize = None
        return fileSize
    except:
        return None


def checkMimeType(fileName):
    fileName = fileName.lower()

    for ext in mimeTypes:
        if fileName.endswith(ext):
            return mimeTypes[ext]
    return None


def err(socket, code, msg):  # 錯誤訊息
    socket.write("HTTP/1.1 "+code+" "+msg+"\r\n\r\n")
    socket.write("<h1>"+msg+"</h1>")


def handleRequest(client):
    req = client.recv(1024).decode('utf8')
    firstLine = req.split('\r\n')[0]  # 取出請求的第一行
    print(firstLine)

    httpMethod = ''
    path = ''

    try:
        httpMethod, path, httpVersion = firstLine.split()  # http方法, 路徑, 版本訊息

        del httpVersion  # 刪除不需要的變數
    except:
        pass

    del firstLine  # 刪除不需要的變數
    del req

    if httpMethod == 'GET':
        fileName = path.strip('/')  # 去除路徑最前變得斜線

        if fileName == '':  # 若是空字串，設成index.html
            fileName = 'index.html'
        sendFile(client, fileName)  # 傳遞檔案給用戶

    else:
        err(client, "501", "Not Implemented")


def sendFile(client, fileName):
    contentType = checkMimeType(fileName)  # 確認檔案類型

    if contentType:  # 如果是支援的檔案類型
        fileSize = checkFileSize(WWWROOT+fileName)

        if fileSize != None:  # 如果檔案存在
            f = open(WWWROOT+fileName, 'r')
            httpHeader.format(contentType, fileSize)
            print('file name: ' + WWWROOT+fileName)

            client.write(httpHeader.encode('utf-8'))

            while True:  # 傳檔案給用戶
                chunk = f.read(64)
                if len(chunk) == 0:
                    break
                client.write(chunk)

            f.close()
        else:
            err(client, "404", "Not Found")
    else:
        err(client, "415", "Unsupported Media Type")


def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print('Web server running on port', PORT)

    while True:
        client = s.accept()[0]

        handleRequest(client)

        client.close()

        print('Free RAM before GC:', gc.mem_free())
        gc.collect()  # 回收記憶體
        print('Free RAM after GC:', gc.mem_free())


main()
