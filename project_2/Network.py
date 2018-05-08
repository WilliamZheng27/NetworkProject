#-*- coding:utf-8 -*-

import socket
import threading
max_listen_num = 5
request_len = 1024


class Network:
    def __init__(self, network_send_port, network_recv_port):
        self.send_port = network_send_port
        self.recv_port = network_recv_port
        self.source_ip = self.get_host_ip()
        self.sock_send = socket.socket()
        self.send_status = 0
        self.target_ip = ''
        self.target_port = 0
        self.sock_recv = socket.socket()
        self.sock_connect = None
        self.recv_status = 0

    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    def connect(self,target_ip,target_port):
        if self.send_status:
            raise Exception('Already connected')
        self.sock_send.connect((target_ip,target_port))
        self.target_ip = target_ip
        self.send_status = 1

    def disconnect(self):
        if not self.send_status:
            raise Exception('Not connected')
        self.sock_send.close()
        self.send_status = 0

    def start_listen(self, call_back_request_handler):
        if self.recv_status:
            raise Exception('Already listening')
        self.sock_recv.bind((self.source_ip, self.recv_port))
        self.sock_recv.listen(max_listen_num)
        t = threading.Thread(target=self.__thread_accept,args=[call_back_request_handler])
        t.start()
        self.recv_status = 1

    def stop_listen(self):
        if not self.recv_status:
            raise Exception('Not listening')
        self.sock_recv.close()
        self.recv_status = 0

    def request(self, target_ip, target_port, method, keep_alive, data=''):
        if not self.send_status:
            self.connect(target_ip,target_port)
        pkg = self.__pack_request(method,target_ip,target_port,len(data),keep_alive,data)
        self.__send(self.sock_send, pkg)
        respose = b''
        respose += self.recieve(self.sock_send,request_len)
        respose = self.__unpack_request(respose)
        body_len = int(respose[6])
        body_buff = self.recieve(self.sock_send,body_len)
        body_buff = body_buff.decode()
        respose += body_buff
        if not keep_alive:
            self.sock_send.close()
        return respose


    def __requestHandler(self,call_back_handler):
        data = b''
        data += self.recieve(self.sock_connect,request_len)
        data = data.decode()
        data = data.split('\r\n')
        ret = data
        keep_alive = int(data[5])
        body_len = int(data[6])
        data = b''
        data += self.recieve(self.sock_connect, body_len)
        body = data.decode()
        ret += body
        call_back_handler(ret)
        if not keep_alive:
            self.sock_connect.close()

    def __thread_accept(self,call_back_request_handler):
        while True:
            self.sock_connect, = self.sock_recv.accept()
            t = threading.Thread(target=self.__requestHandler,args=[call_back_request_handler])
            t.start()

    def __pack_request(self,method,target_ip,target_port,body_len,keep_alive,body):
        respose = ''
        respose += str(method)
        respose += '\r\n'
        respose += self.source_ip
        respose += '\r\n'
        respose += str(self.send_port)
        respose += '\r\n'
        respose += target_ip
        respose += '\r\n'
        respose += str(target_port)
        respose += '\r\n'
        respose += str(keep_alive)
        respose += '\r\n'
        respose += str(body_len)
        respose += '\r\n'
        respose += body
        respose += '\r\n'
        respose = respose.encode()
        return respose

    def __unpack_request(self,buffer):
        buffer.decode()
        buffer = buffer.spilt('\r\n')
        return buffer


    def __pack_respond(self,status_code,target_ip,target_port,body_len,body):
        respose = ''
        respose += str(status_code)
        respose += '\r\n'
        respose += self.source_ip
        respose += '\r\n'
        respose += str(self.send_port)
        respose += '\r\n'
        respose += target_ip
        respose += '\r\n'
        respose += str(target_port)
        respose += '\r\n'
        respose += str(body_len)
        respose += '\r\n'
        respose += body
        respose += '\r\n'
        respose = respose.encode()
        return respose

    def __send(self,sock,data):
        sock.send(data)

    def recieve(self,sock,data_size):
        buffer = b''
        while len(buffer) < data_size:
            buffer += sock.recv(1024)
        return buffer








