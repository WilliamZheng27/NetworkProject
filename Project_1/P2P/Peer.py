import json
import socket
import threading
import os
import math
import time
from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
from flask import make_response
'''
file_sha(string):整个文件的SHA1
seg_sha(list):分块的SHA1列表
    seg in seg_sha:
    seg(string):分块的SHA1
'''


class File:
    def __init__(self, file_sha, file_size, host_enrolled=[]):
        self.file_sha = file_sha
        self.file_size = file_size
        self.host_enrolled = host_enrolled

#获取本机IP
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
#文件目录
base_dir = os.path.dirname(__file__)
source_dir = os.path.join(base_dir,'Download')
# 文件列表
file_list = []
#文件段大小
kilobytes = 1024
megabytes = kilobytes*1000
chunksize = int(1*megabytes)

#Tracker信息
tracker_host = '172.18.34.4'
tracker_port = 10086
#磁盘上存储的文件列表
filelist_name = 'filelist.json'
#本机IP
peer_host = get_host_ip()
peer_port = 10086
peer_recv_port = 51234
p2p_port = 23333
listen_num = 5
#Peer初始化


#命令解析
def commandDispatch(cmd_list):
    cmd_func = cmd_list[0]
    if cmd_func == 'exit':
        disconnectTracker()
    elif cmd_func == 'download':
        file_name = cmd_list[1]
        peer_list = requestFile(file_name)
        file_size = peer_list.pop()
        seg_count = math.ceil(float(file_size) / float(chunksize))
        peer_count = len(peer_list)
        print(seg_count,'segs in total')
        for pe in peer_list:
            print(pe[0] + ' ' + pe[1])
        buffer = b''
        buffer_list = []
        m = 0
        total = 0
        peer_status = []
        for n in range(0,peer_count):
            peer_status.append(0)
        for n in range(0,int(seg_count)):
            buffer_list.append(buffer)
            k = 0
            while True:
                if peer_status[k] == 0:
                    peer_status[k] = 1
                    t = threading.Thread(target=downloadThreadHandler,args=[peer_status,k,buffer_list,peer_list[k][0],int(peer_list[k][1]),file_name,n,n*chunksize,file_size])
                    t.start()
                    break
                k = k + 1
                if k == peer_count:
                    k = 0
        while True:
            temp = 0
            for n in peer_status:
                temp += n
            if not temp:
                break
        print(len(buffer_list),'segs received')
        for buf in buffer_list:
            buffer += buf
        file = open(file_name, 'wb')
        file.write(buffer)
        file.close()



# 读取文件列表
def readFileList():
    for fname in os.listdir(source_dir):
        file_dir = os.path.join(source_dir,fname)
        file_list.append((fname,os.stat(file_dir).st_size))
        print(fname)
#制作请求包
def requestPack(method,request_file,host,port,size=0):
    request = ''
    if int (method) == 0 or int(method) == 1:
        request += method
        request += '\r\n'
        request += '\r\n'
        request += host
        request += '\r\n'
        request += str(port)
        request += '\r\n'
        request += str(size)
        request += '\r\n'
        request += json.dumps(file_list)
        print('requestPack: ', request)
        request = request.encode()
    elif int (method) == 2 or int(method) == 3:
        request += method
        request += '\r\n'
        request += request_file
        request += '\r\n'
        request += host
        request += '\r\n'
        request += str(port)
        request += '\r\n'
        request += str(size)
        request += '\r\n'
        print('requestPack: ', request)
        request = request.encode()
    return request
sock_peer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# 与Tracker建立连接
def connectTracker():
    sock_peer.connect((tracker_host,tracker_port))
    sock_peer.send(requestPack('0',0,peer_host,p2p_port))


# 与Tracker断开连接
def disconnectTracker():
    sock_peer.send(requestPack('1',0,peer_host,p2p_port))
    sock_peer.close()
# 向Tracker请求文件
def requestFile(file):
    #发送请求
    sock_peer.send(requestPack('2',file,peer_host,p2p_port))
    #接受返回值
    buffer = ''
    buffer = sock_peer.recv(1024)
    buffer = buffer.decode()
    response = buffer.split('\r\n')
    print(response)
    #状态码
    status_code = int (response[0])
    #返回的地址
    response_host = response[1]
    #返回的端口
    response_port = int (response[2])
    #返回的File大小
    file_size = int(response[3])
    #返回的File数据（json格式）
    response_data = response[4]
    if status_code == 200:
        peer_list = json.loads(response_data)
        peer_list.append(file_size)
        return peer_list
    elif status_code == 404:
        raise Exception('Connection not found. Connect with Tracker before requesting')

# 向Tracker增加文件
def enrollFile(file_name,file_size):
    sock_peer.send(requestPack('3',file_name,peer_host,p2p_port,file_size))
    time.sleep(1)

#向Peer请求文件
def recieveFile(host,port,file_name,seg_num,total,file_size):
    sock_peer_send = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock_peer_send.connect((host,port))
    request = file_name
    request += '\r\n'
    request += str(seg_num)
    request += '\r\n'
    request = request.encode()
    sock_peer_send.send(request)
    buffer = b''
    while len(buffer) < chunksize and len(buffer) + total < file_size:
        buffer += sock_peer_send.recv(chunksize)
    print(len(buffer), 'bytes')
    print(total,'bytes in total')
    sock_peer_send.close()
    return buffer
#接收其它Peer的请求
def requestHandler(source_dir,sock_peer_recv):
    while True:
        sock_peer_recv_conn, sock_peer_recv_addr = sock_peer_recv.accept()
        t = threading.Thread(target=sendFile,args=[source_dir,sock_peer_recv_conn])
        t.start()
#向其它Peer发送分块
def sendFile(source_dir,sock_peer_recv_conn):
    buffer = b''
    buffer = sock_peer_recv_conn.recv(1024)
    buffer = buffer.decode()
    request = buffer.split('\r\n')
    file = request[0]
    seg_num = int(request[1])
    dir_dst = os.path.join(source_dir,file)
    if not os.path.exists(dir_dst):
        print("File not exist")
    else:
        inputfile = open(dir_dst, 'rb')  # open the fromfile
        chunk = b''
        for num in range(0,seg_num + 1):
            chunk = inputfile.read(chunksize)
        sock_peer_recv_conn.send(chunk)
        inputfile.close()
    sock_peer_recv_conn.close()
#新的下载线程
def downloadThreadHandler(peer_status,peer_num,buffer_list,host,port,file_name,n,total,file_size):
    buffer_list[n] = recieveFile(host, port, file_name, n, total, file_size)
    peer_status[peer_num] = 0

# 初始化本地服务器以运行UI
app = Flask(__name__)

@app.route('/', methods=['GET'])
def UIrequest():
    ins = request.args.get('method')
    print(ins)
    if ins == 'local-files':
        print(file_list)
        return jsonify(file_list)
        #return jsonify(file_list)
if __name__ == '__main__':
    readFileList()
    connectTracker()
    app.run()
    for file in file_list:
        enrollFile(file[0],file[1])
    #初始化监听socket
    sock_peer_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_peer_recv.bind((peer_host,p2p_port))
    sock_peer_recv.listen(listen_num)
    t = threading.Thread(target=requestHandler, args=[source_dir,sock_peer_recv])
    t.start()
    cmd = input('Please enter your command')
    cmd_split = cmd.split(' ')
    commandDispatch(cmd_split)


# TODO:文件分割

# TODO：文件合并
