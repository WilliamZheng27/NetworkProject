import socket
import threading
max_listen_num = 5
request_len = 1024


class Network:
    def __init__(self,network_send_port,network_recv_port,is_running = 1):
        self.send_port = network_send_port
        self.recv_port = network_recv_port
        self.ip_addr = self.get_host_ip()
        if is_running:
            self.start_listen()

    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    def start_listen(self):
        self.sock_recv = socket.socket()
        self.sock_recv.bind((self.ip_addr,self.recv_port))
        self.sock_recv.listen(max_listen_num)
        t = threading.Thread(target=self.thread_accept)
        t.start()

    def stop_listen(self):
        self.sock_recv.close()

    def __requestHandler(self):
        data = self.recv(self.sock_recv,request_len)
        

    def thread_accept(self):
        while True:
            source_ip,source_port = self.sock_recv.accept()
            t = threading.Thread(target=self.__requestHandler)
            t.start()
    def send(self,target_ip,target_port,data,is_need_response = 0):
        self.sock_send = socket.socket()
        self.sock_send.connect((target_ip,target_port))
        self.sock_send.send(data)
        if not is_need_response:
            self.sock_send.close()

    def recv(self,sock,data_size):
        buffer = b''
        while len(buffer) < data_size:
            buffer += sock.recv(1024)
        return buffer








