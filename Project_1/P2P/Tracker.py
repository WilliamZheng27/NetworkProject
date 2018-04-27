import socket
import threading
import json

#节点列表
PeerList = []
#文件列表
FileList = []
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
class Peer:
    def __init__(self,peer_host,peer_port):
        self.peer_host = peer_host
        self.peer_port = peer_port
'''
file_sha:整个文件的SHA1
seg_sha:分块的SHA1
'''
class File:
    def __init__(self,file_sha,host_enrolled=[]):
        self.file_sha = file_sha
        self.host_enrolled = host_enrolled[:]
    def addHost(self,host,port):
        self.host_enrolled.append(Peer(host,port))


'''
host:节点IP(string)
port:节点端口(int)
file:文件列表(list)
    f in file:文件的SHA1
'''



Host = get_host_ip()
Port = 10086

'''TODO:设定定时器，用于更新节点情况
#timer = threading.Timer(60,keepAlive)
timer.start()
'''


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
        内容(json编码)
        '''
        request = buffer.split('\r\n')
        method = int(request[0])
        file_requested = request[1]
        host = request[2]
        port = request[3]
        print(request)
        '''
        处理requet
        0：节点加入
        1：节点断开
        2：请求文件
        3：增加文件
        '''
        ret_code = 200
        ret_data = []
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
                for peer in PeerList:
                    print(peer.peer_host + ' ' + peer.peer_port)
            elif method == 1:
                #移除节点，若不存在抛出异常
                try:
                    print('Connectiong exiting')
                    PeerList.remove(Peer(host,port))
                    for file in FileList:
                        for host_en in file.host_enrolled:
                            if host_en == host:
                                file.host_enrolled.remove(Peer(host,port))
                    print(PeerList)
                    flag = 1
                    sock.close()
                except ValueError:
                    raise Exception("Host Not Found")
            elif method == 2:
                print('Requesting File')
                for file in FileList:
                    if file.file_sha == file_requested:
                        print(file.file_sha)
                        for peer_en in file.host_enrolled:
                            ret_data.append((peer_en.peer_host,peer_en.peer_port))
                # 构造返回报文
                print(ret_code)
                print(Host)
                print(Port)
                print(ret_data)
                ret_msg += str(ret_code)
                ret_msg += '\r\n'
                ret_msg += Host
                ret_msg += '\r\n'
                ret_msg += str(Port)
                ret_msg += '\r\n'
                ret_msg += json.dumps(ret_data)
                print(ret_msg)
                ret_msg = ret_msg.encode()
                sock.send(ret_msg)
            elif method == 3:
                print("Enrolling")
                for file in FileList:
                    if file.file_sha == file_requested:
                        file.host_enrolled.append(Peer(host,port))
                new_file = File(file_requested)
                new_file.addHost(host,port)
                FileList.append(new_file)
                for files in FileList:
                    print(files.file_sha)
                    print(files.host_enrolled)
                    for hh in files.host_enrolled:
                        print(hh.peer_host + ' ' + hh.peer_port)
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
        if flag:
            break


    

#TODO:更新Peer列表与文件列表
#def keepAlive()

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