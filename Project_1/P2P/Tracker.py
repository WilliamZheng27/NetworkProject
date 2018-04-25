import socket
import threading
import struct
import json
#节点及资源列表
DataList = []
'''
file_sha:整个文件的SHA1
seg_sha:分块的SHA1
'''
class File:
    def __init__(file_sha,seg_sha):
        self.file_sha = file_sha
        self.seg_sha = seg_sha
'''
host:节点IP
port:节点端口
file_sha:文件列表
'''
class Data:
    def __init__(host,port,file):
        self.host = host
        self.port = port
        self.file = file

Host = '172.18.34.4'
Port = '10086'
#服务器初始化
sock_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock_server.bind(Host,Port)
sock_server.listen(5)
#设定定时器，用于更新节点情况
timer = threading.Timer(60,keepAlive)
timer.start()
#接收请求
def Main():
    while True:
        sock,addr = sock_server.accept()
    #创建新线程以处理TCP连接
    t = threading.Thread(target=ConnectionHandler, args=(sock, addr))
    t.start()
#处理TCP连接
def ConnectionHandler(sock,addr):
    #接收数据
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
    协议版本：
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
    try:
        if (request == 0):
            #监测节点是否已经存在
            for Data in DataList:
                if Data.host == host:
                    raise Exception("Same Host")
            #将节点加入列表
            DataList.append(Data(host,port,body))
        else if request == 1:
            #移除节点，若不存在抛出异常
            Obj = Data(host,port,body)
            try:
                DataList.remove(Data)
            except ValueError:
                raise Exception("Host Not Found")
        else if request == 2:
            RetData = []
            for Peer in DataList:
                for file in Peer.file:
                    if file.file_sha == file_requested:
                        RetData.append(Peer.host,Peer.port,file.seg_sha)
        else if request == 3:
            for Peer in DataList:
                if Peer.host == host and Peer.port == port:
                    Peer.file += body
            raise Exception("Host Not Found")
        RetCode = 200
    except Exception,'Same Host':
        RetCode = 403
    except Exception,"Host Not Found":
        RetCode = 404
    finally:
        '''
        返回报文结构
        状态码(int)
        主机(string)
        端口(int)
        返回数据(json)
        '''
        #构造返回报文
        RetMsg = ''
        RetMsg += RetCode
        RetMsg +='\r\n'
        RetMsg += Host
        RetMsg += '\r\n'
        RetMsg += Port
        RetMsg += '\r\n'
        RetMsg += json.dump(RetData)





    


def KeepAlive():

