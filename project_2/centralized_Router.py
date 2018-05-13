# -*- coding:utf-8 -*-
import LS_Network
import socket
import json
import copy
import time

Method_Route_Msg = '0'
Method_Data_Pack = '1'
Method_Request_Route = '2'
Method_Topo_Msg = '3'
Method_Exit_Msg = '4'


class Router:
    def __init__(self, send_port, recv_port, link_table):
        self.routingTable = {}
        self.link_table = link_table
        self.send_port = send_port
        self.recv_port = recv_port
        self.network_obj = LS_Network.Network(send_port, recv_port)

    # TODO: 转发数据包


class CenterServer():
    def __init__(self, send_port, recv_port):
        '''
        global_topo: 字典结构，全局拓扑图，key=路由器IP，value=列表结构，元素为列表结构[链路距离, 邻接路由IP]

        global_routing_table: 字典结构，全局路由表（每个路由器的路由表）
        其中：key=路由器IP，value=列表结构, 元素为路由表项，列表结构[key=目的IP，value=下一跳路由IP]
        '''
        self.send_port = send_port
        self.recv_port = recv_port
        self.network_obj = LS_Network.Network(send_port, recv_port)
        self.global_topo = {}
        self.global_routing_table = {}
        self.listen_router_link_table()
        time.sleep(10)
        while self.network_obj.thread_number != 0:
            time.sleep(5)
        self.test_router()
        self.LS()
        self.send_routing_table()
        for key, value in self.global_routing_table.items():
            print(key, '路由：', value)

    def Dijkstra(self, source_ip, dest_ip):
        length = {}
        set = []
        pathto = {source_ip: None}
        for key in self.global_topo.keys():
            length[key] = 9999
        length[0] = 9999
        length[source_ip] = 0
        while dest_ip not in set:
            min = 0
            for key in self.global_topo.keys():
                if key not in set and length[key] < length[min]:
                    min = key
            set.append(min)
            for edge in self.global_topo[min]:
                v = edge[1]
                if v not in set:
                    lenn = edge[0]
                    newlen = lenn + length[min]
                    if newlen < length[v]:
                        length[v] = newlen
                        pathto[v] = min
        e = pathto[dest_ip]
        stack = []
        while e != None:
            stack.append(e)
            e = pathto[e]
        for i in range(0, len(stack)):
            if i == 0:
                if [dest_ip, dest_ip] not in self.global_routing_table[stack[i]]:
                    self.global_routing_table[stack[i]].append([dest_ip, dest_ip])
            else:
                if [dest_ip, stack[i - 1]] not in self.global_routing_table[stack[i]]:
                    self.global_routing_table[stack[i]].append([dest_ip, stack[i - 1]])

    # 根据全局拓扑图global_topo生成全局路由表
    def LS(self):
        for ip in self.global_topo.keys():
            self.global_routing_table[ip] = []
        for source_ip in self.global_topo.keys():
            for dest_ip in self.global_topo.keys():
                if source_ip != dest_ip:
                    self.Dijkstra(source_ip, dest_ip)

    def __msg_handler(self, msg):
        if msg[0] == Method_Topo_Msg:
            self.create_global_topo(msg)

    # 生成全局拓扑图global_topo
    def create_global_topo(self, msg):
        self.global_topo[msg[1]] = msg[7]

    # 接收各个路由器的link_table
    def listen_router_link_table(self):
        self.network_obj.LS_start_listen(self.__msg_handler)

    # 将生成的全局路由表发往各个路由器
    def send_routing_table(self):
        for router_ip in self.global_routing_table.keys():
            data = json.dumps(self.global_routing_table[router_ip])
            self.network_obj.seng_data(router_ip, self.recv_port, 0, 0, data)

    def test_router(self):
        routers = []
        for key in self.global_topo.keys():
            routers.append(key)
        for key in self.global_topo.keys():
            for value in self.global_topo[key]:
                if value[1] not in routers:
                    self.global_topo[key].remove([value[0], value[1]])


class RouterLS(Router):
    '''
    routingTable: 路由表为字典结构，key=目的路由IP，value=下一条路由IP
    '''
    def __init__(self, send_port, recv_port, center_server_ip, link_table):
        Router.__init__(self, send_port, recv_port, link_table)
        self.center_server_ip = center_server_ip
        self.send_link_table()
        self.recv_routing_table()
        time.sleep(10)
        while self.network_obj.thread_number != 0:
            time.sleep(5)

    def __msg_handler(self, msg):
        if msg[0] == Method_Route_Msg:
            self.create_routing_table(msg)

    # 生成路由表
    def create_routing_table(self, msg):
        for item in msg[7]:
            self.routingTable[item[0]] = item[1]

    # 接收来自CenterServer的路由表
    def recv_routing_table(self):
        self.network_obj.LS_start_listen(self.__msg_handler)

    # 向CenterServer发送link_table
    def send_link_table(self):
        data = []
        for key in self.link_table.keys():
            data.append([self.link_table[key][1], key])
        data = json.dumps(data)
        self.network_obj.seng_data(self.center_server_ip, self.recv_port, 3, 0, data)
