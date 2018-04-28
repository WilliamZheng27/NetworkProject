import socket
import threading
import json

#节点列表
PeerList = []
#文件列表
FileList = []
#获取本机IP
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
#Peer节点类
class Peer:
    def __init__(self,peer_host,peer_port):
        self.peer_host = peer_host
        self.peer_port = peer_port
'''
file_sha:文件名
file_size:文件大小
host_enrolled:拥有该文件的Peer
addHost:增加新的Peer
'''
class File:
    def __init__(self,file_sha,file_size,host_enrolled=[]):
        self.file_sha = file_sha
        self.file_size = file_size
        self.host_enrolled = host_enrolled[:]
    def addHost(self,host,port):
        self.host_enrolled.append(Peer(host,port))
#本机IP
Host = get_host_ip()
#用于侦听Peer连接的端口
Port = 10086


#处理TCP连接
def connectionHandler(sock):
    flag = 0
    while True:
        print('Connection received')
        #接收数据
        buffer = b''
        buffer = sock.recv(1024)
        buffer = buffer.decode()
        print(buffer)
        #解析请求
        '''
        协议格式
        头部
        请求类型:
        请求的文件：
        主机：
        端口：
        文件大小：
        内容(json编码)
        '''
        request = buffer.split('\r\n')
        method = int(request[0])
        file_requested = request[1]
        host = request[2]
        port = request[3]
        file_size = int(request[4])
        print(request)
        '''
        处理requet
        0：节点加入
        1：节点断开
        2：请求文件
        3：增加文件
        '''
        '''
        返回信息
        状态码：
        地址：
        端口：
        请求的文件的大小：
        返回的数据（json格式）
        '''
        #状态码
        ret_code = 200
        #返回的数据
        ret_data = []
        #请求的文件的大小
        ret_size = 0
        #返回报文
        ret_msg = ''
        try:
            if method == 0:
                print('Connecting to peer')
                #监测节点是否已经存在
                for peer in PeerList:
                    if peer.host == host:
                        raise Exception("Same Host")
                #将节点加入列表
                PeerList.append(Peer(host,port))
            elif method == 1:
                #移除节点，若不存在抛出异常
                try:
                    print('Connectiong exiting')
                    #从节点列表中移除节点
                    PeerList.remove(Peer(host,port))
                    #从文件列表中移除节点
                    for file in FileList:
                        for host_en in file.host_enrolled:
                            if host_en == host:
                                file.host_enrolled.remove(Peer(host,port))
                    #设置关闭标志
                    flag = 1
                    sock.close()
                except ValueError:
                    raise Exception("Host Not Found")
            #请求文件
            elif method == 2:
                print('Requesting File')
                #查找被请求的文件
                for file in FileList:
                    if file.file_sha == file_requested:
                        #返回文件的大小
                        ret_size = file.file_size
                        #返回含有此文件的Peer列表
                        for peer_en in file.host_enrolled:
                            ret_data.append((peer_en.peer_host,peer_en.peer_port))
                # 构造返回报文
                ret_msg += str(ret_code)
                ret_msg += '\r\n'
                ret_msg += Host
                ret_msg += '\r\n'
                ret_msg += str(Port)
                ret_msg += '\r\n'
                ret_msg += str(ret_size)
                ret_msg += '\r\n'
                ret_msg += json.dumps(ret_data)
                print(ret_msg)
                ret_msg = ret_msg.encode()
                sock.send(ret_msg)
            #向服务器声明拥有某文件
            elif method == 3:
                #设置flag
                flag_ext = 0
                print("Enrolling")
                #在文件列表中查找该文件
                for file in FileList:
                    if file.file_sha == file_requested:
                        flag_ext = 1
                        #添加该Peer到文件信息中
                        file.host_enrolled.append(Peer(host,port))
                #文件列表中没有该文件，添加到文件列表中
                if not flag_ext:
                    new_file = File(file_requested,file_size)
                    new_file.addHost(host,port)
                    FileList.append(new_file)
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
        #若关闭标志被设定，则断开Tracker与该Peer的连接
        if flag:
            break




if __name__ == '__main__':
    # 服务器初始化
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_server.bind((Host, Port))
    sock_server.listen(5)
    # 接收请求
    while True:
        sock, addr = sock_server.accept()
        # 创建新线程以处理TCP连接
        t = threading.Thread(target=connectionHandler, args=[sock])
        t.start()