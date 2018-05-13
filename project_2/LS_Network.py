# -*- coding:utf-8 -*-

import socket
import threading
import json

max_listen_num = 5
LS_head_len = 59
pkg_head_len = 73


class Network:
    def __init__(self, network_send_port, network_recv_port):
        self.send_port = network_send_port
        self.recv_port = network_recv_port
        self.source_ip = self.get_host_ip()
        self.sock_send = socket.socket()
        self.target_ip = ''
        self.target_port = 0
        self.sock_recv = socket.socket()
        self.sock_connect = {}
        self.thread_number = 0
        self.pkg_thread_number = 0

    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    def connect(self, target_ip, target_port):
        self.sock_send = socket.socket()
        self.sock_send.connect((target_ip, target_port))
        self.target_ip = target_ip

    def __send(self, sock, data):
        sock.send(data)

    def LS_start_listen(self, call_back_request_handler):
        self.sock_recv.bind((self.source_ip, self.recv_port))
        self.sock_recv.listen(max_listen_num)
        t = threading.Thread(target=self.LS__thread_accept, args=[call_back_request_handler])
        t.start()

    def seng_data(self, target_ip, target_port, method, keep_alive, data=''):
        self.connect(target_ip, target_port)
        pkg = self.LS__pack_request(method, target_ip, target_port, len(data), keep_alive, data)
        self.__send(self.sock_send, pkg)
        if not keep_alive:
            self.sock_send.close()

    def LS__thread_accept(self, call_back_request_handler):
        while True:
            tmp_obj, ipadrs = self.sock_recv.accept()
            self.sock_connect[ipadrs[0]] = tmp_obj
            t = threading.Thread(target=self.LS__requestHandler, args=[ipadrs[0], call_back_request_handler])
            t.start()
            self.thread_number += 1

    def LS__requestHandler(self, ip, call_back_handler):
        data = b''
        data += self.LS_recieve(self.sock_connect[ip], LS_head_len)
        data = data.decode()
        data = data.split('\r\n')
        ret = data
        keep_alive = int(data[5])
        body_len = int(data[6])
        data = b''
        data += self.LS_recieve(self.sock_connect[ip], body_len)
        body = json.loads(data.decode())
        ret[7] = body
        call_back_handler(ret)
        if not keep_alive:
            self.sock_connect[ip].close()
            del self.sock_connect[ip]
        self.thread_number -= 1

    def LS__pack_request(self, method, target_ip, target_port, body_len, keep_alive, body):
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
        if 9 < body_len < 100:
            respose += str(0)
        elif body_len < 10:
            respose += str(0)
            respose += str(0)
        respose += str(body_len)
        respose += '\r\n'
        respose += body
        respose = respose.encode()
        return respose

    def LS_recieve(self, sock, data_size):
        buffer = b''
        while len(buffer) < data_size:
            buffer += sock.recv(data_size)
        return buffer

    def send_pkg(self, target_ip, target_port, method, keep_alive, finial_dest_ip, data=''):
        self.connect(target_ip, target_port)
        pkg = self.LS__pack_pkg(method, target_ip, target_port, len(data), keep_alive, finial_dest_ip, data='')
        self.__send(self.sock_send, pkg)
        if not keep_alive:
            self.sock_send.close()

    def LS__pack_pkg(self, method, target_ip, target_port, data_length, keep_alive, finial_dest_ip, data=''):
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
        if 9 < data_length < 100:
            respose += str(0)
        elif data_length < 10:
            respose += str(0)
            respose += str(0)
        respose += str(data_length)
        respose += '\r\n'
        respose += finial_dest_ip
        respose += '\r\n'
        print(len(respose.encode()))
        respose += data
        respose = respose.encode()
        return respose

    def LS_start_listen_pkg(self):
        self.sock_recv.bind((self.source_ip, self.recv_port))
        self.sock_recv.listen(max_listen_num)
        t = threading.Thread(target=self.LS__thread_accept_pkg)
        t.start()

    def LS__thread_accept_pkg(self):
        while True:
            tmp_obj, ipadrs = self.sock_recv.accept()
            self.sock_connect[ipadrs[0]] = tmp_obj
            t = threading.Thread(target=self.LS__pkgHandler, args=[ipadrs[0]])
            t.start()
            self.pkg_thread_number += 1

    def LS__pkgHandler(self, ip):
        data = b''
        data += self.LS_recieve(self.sock_connect[ip], pkg_head_len)
        data = data.decode()
        data = data.split('\r\n')
        next_jmp = data[3]
        keep_alive = int(data[5])
        body_len = int(data[6])
        final_dest_ip = data[7]
        data = b''
        data += self.LS_recieve(self.sock_connect[ip], body_len)
        body = json.loads(data.decode())
        if final_dest_ip == self.source_ip:
            # TODO:发往客户端
            pass
        else:
            self.send_pkg(next_jmp, self.recv_port, 1, 0, final_dest_ip, json.dumps(body))
        if not keep_alive:
            self.sock_connect[ip].close()
            del self.sock_connect[ip]
        self.pkg_thread_number -= 1
