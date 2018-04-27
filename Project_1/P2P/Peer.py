import json
import socket
'''
file_sha(string):整个文件的SHA1
seg_sha(list):分块的SHA1列表
    seg in seg_sha:
    seg(string):分块的SHA1
'''


class File:
    def __init__(self, file_sha, seg_sha):
        self.file_sha = file_sha
        self.seg_sha = seg_sha


# 文件列表
file_list = []
#Tracker信息
tracker_host = '172.18.34.4'
tracker_port = 10086
#磁盘上存储的文件列表
filelist_name = 'filelist.json'
#本机IP
peer_host = get_host_ip()
peer_port = 10086
p2p_port = 23333
listen_num = 5
#Peer初始化
def main():
    readFileList()
    connectTracker()
    #初始化监听socket
    sock_peer_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_peer_recv.bind(peer_host,p2p_port)
    sock_peer_recv.listen(listen_num)


#获取本机IP
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
# 读取文件列表
def readFileList():
    try:
        with open(filelist_name, 'rw') as file_obj:
            file_list = json.loads(file_obj)
    except IOError as err:
        print('Error occured when reading file list.')
#制作请求包
def requestPack(method,request_file,host,port):
    request = ''
    if method == 0 or method == 1 or method == 3:
        request += method
        request += '\r\n'
        request += '\r\n'
        request += host
        request += '\r\n'
        request += port
        request += '\r\n'
        request += json.dumps(file_list)
    elif method == 2:
        request += method
        request += '\r\n'
        request += request_file
        request += '\r\n'
        request += host
        request += '\r\n'
        request += port
        request += '\r\n'
    return request
sock_peer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# 与Tracker建立连接
def connectTracker():
    sock_peer.connect((tracker_host,tracker_port))
    sock_peer.send(requestPack(0,0,peer_host,peer_port))

# 与Tracker断开连接
def disconnectTracker():
    sock_peer.send(requestPack(1,0,peer_host,peer_port))
    sock_peer.close()
# 向Tracker请求文件
def requestFile(file):
    #发送请求
    sock_peer.send(requestPack(2,file,peer_host,peer_port))
    #接受返回值
    buffer = ''
    while True:
        d = sock_peer.recv(1024)
        if d:
            buffer += d
        else:
            break
    response = buffer.split('\r\n')
    #状态码
    status_code = response[0]
    #返回的地址
    response_host = response[1]
    #返回的端口
    response_port = response[2]
    #返回的Peer数据（json格式）
    response_data = response[3]
    if status_code == 200:
        peer_list = json.loads(response_data)
        return peer_list
    elif status_code == 404:
        raise Exception('Connection not found. Connect with Tracker before requesting')

# TODO：向Tracker增加文件

# TODO：向Peer请求文件
def recieveFile(peer_list):
    peer_list = []
    for peer in peer_list:


#TODO:接受其它Peer的请求
def sendFile(file,seg_num):


# TODO:文件分割

# TODO：文件合并
