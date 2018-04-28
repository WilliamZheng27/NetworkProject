import json
import socket
import threading
import os
import math
import time


class File:
    '''
    定义File类，包含的属性如下：
    file_sha: 整个文件的SHA1
    file_size: 整个文件的大小
    host_enrolled: 具有该文件的主机的IP地址和端口
    '''

    def __init__(self, file_sha, file_size, host_enrolled=[]):
        self.file_sha = file_sha
        self.file_size = file_size
        self.host_enrolled = host_enrolled


# 获取本机IP
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


# 文件目录
base_dir = os.path.dirname(__file__)
source_dir = os.path.join(base_dir, 'Download')

# 文件列表
file_list = []

# 文件段大小设置为1MB
kilobytes = 1024
megabytes = kilobytes * 1000
chunksize = int(1 * megabytes)

# Tracker信息
tracker_host = '172.18.34.4'
tracker_port = 10086

# 磁盘上存储的文件列表
filelist_name = 'filelist.json'

# 本机IP
peer_host = get_host_ip()
peer_port = 10086
peer_recv_port = 51234
p2p_port = 23333
listen_num = 5


# 命令解析
def commandDispatch(cmd_list):
    cmd_func = cmd_list[0]

    # exit：与Tracker断开连接
    if cmd_func == 'exit':
        disconnectTracker()

    # download：下载目的文件
    elif cmd_func == 'download':

        # 获取文件名
        file_name = cmd_list[1]

        # 获取具有该文件的主机列表
        peer_list = requestFile(file_name)

        # 获取该文件的大小
        file_size = peer_list.pop()

        # 计算分割该文件后所得的总分块数
        seg_count = math.ceil(float(file_size) / float(chunksize))

        # 计算具有该文件的主机总数
        peer_count = len(peer_list)

        print(seg_count, 'segs in total')
        for pe in peer_list:
            print(pe[0] + ' ' + pe[1])
        buffer = b''
        buffer_list = []
        m = 0
        total = 0
        peer_status = []

        # 初始化peer的状态列表
        for n in range(0, peer_count):
            peer_status.append(0)

        # 初始化缓冲列表
        for n in range(0, int(seg_count)):
            buffer_list.append(buffer)
            k = 0
            while True:

                # peer状态为0时开始传输
                if peer_status[k] == 0:
                    peer_status[k] = 1

                    # 为每个peer的传输建立新的线程
                    t = threading.Thread(target=downloadThreadHandler,
                                         args=[peer_status, k, buffer_list, peer_list[k][0], int(peer_list[k][1]),
                                               file_name, n, n * chunksize, file_size])
                    t.start()
                    break
                k = k + 1
                if k == peer_count:
                    k = 0

        # 传输轮转直至传输完毕
        while True:
            temp = 0
            for n in peer_status:
                temp += n
            if not temp:
                break
        print(len(buffer_list), 'segs received')

        # 将所有接收的缓存组合
        for buf in buffer_list:
            buffer += buf

        # 将所有接收的数据写入文件
        file = open(file_name, 'wb')
        file.write(buffer)
        file.close()


# 读取文件列表
def readFileList():
    for fname in os.listdir(source_dir):
        file_dir = os.path.join(source_dir, fname)
        file_list.append((fname, os.stat(file_dir).st_size))
        print(fname)


# 制作请求包
def requestPack(method, request_file, host, port, size=0):
    request = ''

    # 制作0、1（method）的请求包
    if int(method) == 0 or int(method) == 1:
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

    # 制作2、3（method）的请求包
    elif int(method) == 2 or int(method) == 3:
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


sock_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# 与Tracker建立连接
def connectTracker():
    sock_peer.connect((tracker_host, tracker_port))
    sock_peer.send(requestPack('0', 0, peer_host, p2p_port))


# 与Tracker断开连接
def disconnectTracker():
    sock_peer.send(requestPack('1', 0, peer_host, p2p_port))
    sock_peer.close()


# 向Tracker请求文件
def requestFile(file):
    # 发送请求
    sock_peer.send(requestPack('2', file, peer_host, p2p_port))

    # 接受返回值
    buffer = ''
    buffer = sock_peer.recv(1024)
    buffer = buffer.decode()
    response = buffer.split('\r\n')
    print(response)

    # 状态码
    status_code = int(response[0])

    # 返回的地址
    response_host = response[1]

    # 返回的端口
    response_port = int(response[2])

    # 返回的File大小
    file_size = int(response[3])

    # 返回的File数据（json格式）
    response_data = response[4]
    if status_code == 200:
        peer_list = json.loads(response_data)
        peer_list.append(file_size)
        return peer_list
    elif status_code == 404:
        raise Exception('Connection not found. Connect with Tracker before requesting')


# 向Tracker增加文件
def enrollFile(file_name, file_size):
    sock_peer.send(requestPack('3', file_name, peer_host, p2p_port, file_size))
    time.sleep(1)


# 向Peer请求文件
def recieveFile(host, port, file_name, seg_num, total, file_size):
    sock_peer_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_peer_send.connect((host, port))

    # 制作请求头
    request = file_name
    request += '\r\n'
    request += str(seg_num)
    request += '\r\n'
    request = request.encode()

    # 发送请求头
    sock_peer_send.send(request)

    # 接收其他peer传来的数据
    buffer = b''
    while len(buffer) < chunksize and len(buffer) + total < file_size:
        buffer += sock_peer_send.recv(chunksize)
    print(len(buffer), 'bytes')
    print(total, 'bytes in total')

    # 接收完相应块后断开连接
    sock_peer_send.close()

    # 返回所接收的数据块
    return buffer


# 接收其它Peer的请求
def requestHandler(source_dir, sock_peer_recv):
    while True:
        sock_peer_recv_conn, sock_peer_recv_addr = sock_peer_recv.accept()

        # 为每个连接请求建立一个新的线程
        t = threading.Thread(target=sendFile, args=[source_dir, sock_peer_recv_conn])
        t.start()


# 向其它Peer发送分块
def sendFile(source_dir, sock_peer_recv_conn):
    # 接收peer的请求报文
    buffer = b''
    buffer = sock_peer_recv_conn.recv(1024)
    buffer = buffer.decode()

    # 解析请求报文
    request = buffer.split('\r\n')
    file = request[0]
    seg_num = int(request[1])
    dir_dst = os.path.join(source_dir, file)

    # 若文件不存在则显示错误信息
    if not os.path.exists(dir_dst):
        print("File not exist")

    # 若文件存在则传送相应的文件块
    else:

        # 读取相应的文件块
        inputfile = open(dir_dst, 'rb')  # open the fromfile
        chunk = b''
        for num in range(0, seg_num + 1):
            chunk = inputfile.read(chunksize)

        # 发送该文件块后断开连接
        sock_peer_recv_conn.send(chunk)
        inputfile.close()
    sock_peer_recv_conn.close()


# 新的下载线程
def downloadThreadHandler(peer_status, peer_num, buffer_list, host, port, file_name, n, total, file_size):
    buffer_list[n] = recieveFile(host, port, file_name, n, total, file_size)
    peer_status[peer_num] = 0


# Peer初始化
if __name__ == '__main__':

    # 读取文件列表
    readFileList()

    # 连接tracker
    connectTracker()

    # 将本地的文件列表传给traker
    for file in file_list:
        enrollFile(file[0], file[1])

    # 初始化监听socket
    sock_peer_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_peer_recv.bind((peer_host, p2p_port))
    sock_peer_recv.listen(listen_num)

    # 为每个peer文件请求建立新的线程
    t = threading.Thread(target=requestHandler, args=[source_dir, sock_peer_recv])
    t.start()

    # 读取用户输入并解析
    cmd = input('Please enter your command')
    cmd_split = cmd.split(' ')
    commandDispatch(cmd_split)
