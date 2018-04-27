import socket
import threading
import json

#节点列表
PeerList = []
#文件列表
FileList = []

class Peer:
    def __init__(self,peer_host,peer_port):
        self.peer_host = peer_host
        self.peer_port = peer_port
'''
file_sha:整个文件的SHA1
seg_sha:分块的SHA1
'''
class File:
    def __init__(self,file_sha,seg_sha):
        self.file_sha = file_sha
        self.seg_sha = seg_sha


'''
host:节点IP(string)
port:节点端口(int)
file:文件列表(list)
    f in file:文件的SHA1
'''



Host = '172.18.34.4'
Port = '10086'
#服务器初始化
sock_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock_server.bind(Host,Port)
sock_server.listen(5)
'''TODO:设定定时器，用于更新节点情况
#timer = threading.Timer(60,keepAlive)
timer.start()
'''

#接收请求
def main():
    while True:
        sock, addr = sock_server.accept()
        #创建新线程以处理TCP连接
        t = threading.Thread(connectionHandler,sock)
        t.start()
#处理TCP连接
def connectionHandler(sock):
    #接收数据
    buffer = ''
    while True:
        d = sock.recv(1024)
        if d:
            buffer.append(d)
        else:
            break
    #解析请求
    '''
    协议格式
    头部
    请求类型:
    请求的文件：
    主机：
    端口：
    内容(json编码)
    '''
    request = buffer.split('\r\n')
    method = request[0]
    file_requested = request[1]
    host = request[2]
    port = request[3]
    body = json.load(request[4])

    '''
    处理requet
    0：节点加入
    1：节点断开
    2：请求文件
    3：增加文件
    '''
    ret_code = 200
    ret_data = []
    try:
        if method == 0:
            #监测节点是否已经存在
            for Peer in PeerList:
                if Peer.host == host:
                    raise Exception("Same Host")
            #将节点加入列表
            PeerList.append(Peer(host,port))
        elif method == 1:
            #移除节点，若不存在抛出异常
            try:
                PeerList.remove(Peer(host,port))
                sock.close()
            except ValueError:
                raise Exception("Host Not Found")
        elif method == 2:
            for file in FileList:
                if file.file_sha == file_requested:
                    ret_data.append(file)

        elif method == 3:
            for file in FileList:
                if file.file_sha == file_requested:
                    file.seg_sha += body
            raise Exception("Host Not Found")

    except Exception as e:
        if e == 'Same Host':
            ret_code = 403
        elif e == 'Host Not Found':
            ret_code = 404

    finally:
        '''
        返回报文结构
        状态码(int)
        主机(string)
        端口(int)
        返回数据(json)
        '''
        #构造返回报文
        ret_msg = ''
        ret_msg += ret_code
        ret_msg += '\r\n'
        ret_msg += Host
        ret_msg += '\r\n'
        ret_msg += Port
        ret_msg += '\r\n'
        ret_msg += json.dump(ret_data)
        sock.send(ret_msg)

    

#TODO:更新Peer列表与文件列表
#def keepAlive()
