import json
import socket
import threading
import os
'''
file_sha(string):整个文件的SHA1
seg_sha(list):分块的SHA1列表
    seg in seg_sha:
    seg(string):分块的SHA1
'''


class File:
    def __init__(self, file_sha, host_enrolled=[]):
        self.file_sha = file_sha
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
chunksize = int(200*megabytes)
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
        for pe in peer_list:
            print(pe[0] + ' ' + pe[1])
        n = 0
        buffer = b''
        for peer_en in peer_list:
            buffer += recieveFile(peer_en[0],int(peer_en[1]),file_name,n)
            n = n + 1
        file = open(file_name, 'wb')
        file.write(buffer)
        file.close()



# 读取文件列表
def readFileList():
    for fname in os.listdir(source_dir):
        file_list.append(fname)
        print(fname)
#制作请求包
def requestPack(method,request_file,host,port):
    request = ''
    if int (method) == 0 or int(method) == 1:
        request += method
        request += '\r\n'
        request += '\r\n'
        request += host
        request += '\r\n'
        request += str(port)
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
    #返回的File数据（json格式）
    response_data = response[3]
    if status_code == 200:
        peer_list = json.loads(response_data)
        return peer_list
    elif status_code == 404:
        raise Exception('Connection not found. Connect with Tracker before requesting')

# 向Tracker增加文件
def enrollFile(file_name):
    sock_peer.send(requestPack('3',file_name,peer_host,p2p_port))

#向Peer请求文件
def recieveFile(host,port,file_name,seg_num):
    sock_peer_recv = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock_peer_recv.connect((host,port))
    request = file_name
    request += '\r\n'
    request += str(seg_num)
    request += '\r\n'
    request = request.encode()
    sock_peer_recv.send(request)
    buffer = sock_peer_recv.recv(chunksize)
    sock_peer_recv.close()
    return buffer


#接受其它Peer的请求
def sendFile(source_dir,sock_peer_recv):
    sock_peer_recv_conn,sock_peer_recv_addr = sock_peer_recv.accept()
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

if __name__ == '__main__':
    readFileList()
    connectTracker()
    for file in file_list:
        enrollFile(file)
    #初始化监听socket
    sock_peer_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_peer_recv.bind((peer_host,p2p_port))
    sock_peer_recv.listen(listen_num)
    t = threading.Thread(target=sendFile, args=[source_dir,sock_peer_recv])
    t.start()
    cmd = input('Please enter your command')
    cmd_split = cmd.split(' ')
    commandDispatch(cmd_split)




# TODO:文件分割

# TODO：文件合并
