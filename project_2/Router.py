#-*- coding:utf-8 -*-
import Network
import json

class Router:
    def __init__(self,send_port,recv_port,link_table,router_routingTable=None):
        self.routingTable = router_routingTable
        self.link_table = link_table
        self.send_port = send_port
        self.recv_port = recv_port
        self.network_obj = Network.Network(send_port,recv_port)

    #转发数据包
    def routing(self, pkg):
        dest_ip = pkg.decode().split('\r\n')[3]
        dest_port = int(pkg.decode().split('\r\n')[4])
        next_jmp = self.routingTable.get(dest_ip)
        if next_jmp is None:
            raise Exception,'Unknown Destination'
        self.network_obj.request(next_jmp,dest_port,1,0,pkg)
        return

class Router_DV(Router):
    def __init__(self, send_port, recv_port, router_routingTable=None):
        Router.__init__(self,send_port,recv_port,router_routingTable)
        self.network_obj.start_listen(self.__msg_handler)
    #发送本路由的路由信息
    def send_routing_msg(self):
        for rt in self.link_table:
            #逆转毒性处理
            de_possion = self.routingTable
            de_possion[rt] = 9999
            #发送本机路由表
            self.network_obj.request(rt, self.recv_port, 0, 0, json.dumps(de_possion))
        return

    def __msg_handler(self, msg):
        if msg[0] == 0:
            self.routing(msg)
        elif msg[0] == 1:
            self.recv_routing_msg(msg)
        elif msg[0] == 2:
            self.send_routing_msg()
        return
    #接受其它路由的路由信息
    def recv_routing_msg(self, msg):
        dist = self.routingTable.get(msg[1])
        neibor_dict = json.loads(msg[7])
        flag = 0
        for key in neibor_dict.key():
            if dist + neibor_dict.get(key) < self.routingTable.get(key):
                flag = 1
                self.routingTable[key] = dist + neibor_dict.get(key)
        #向其他路由发送更新后的路由表
        if flag:
            self.send_routing_msg()
        return







