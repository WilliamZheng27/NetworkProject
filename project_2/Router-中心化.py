# -*- coding:utf-8 -*-
import Network
import socket
import json
import copy

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
        self.network_obj = Network.Network(send_port, recv_port)

    # 转发数据包
    def routing(self, pkg):
        dest_ip = pkg.decode().split('\r\n')[3]
        dest_port = int(pkg.decode().split('\r\n')[4])
        next_jmp = self.routingTable.get(dest_ip)
        if next_jmp is None:
            raise Exception('Unknown Destination')
        self.network_obj.request(next_jmp, dest_port, 1, 0, pkg)
        return


# TODO:中心服务器
class CenterServer():
    def __init__(self, send_port, recv_port):
        '''
        global_topo: 字典结构，全局拓扑图，key=路由器IP，value=列表结构，元素为[链路距离, 邻接路由IP]

        global_routing_table: 字典结构，全局路由表（每个路由器的路由表）
        其中：key=路由器IP，value=列表结构, 元素为路由表项，字典结构{key=目的IP，value=下一跳路由IP}
        '''
        self.send_port = send_port
        self.recv_port = recv_port
        self.global_topo = {}
        self.global_routing_table = {}

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
                if {dest_ip: dest_ip} not in self.global_routing_table[stack[i]]:
                    self.global_routing_table[stack[i]].append({dest_ip: dest_ip})
            else:
                if {dest_ip: stack[i - 1]} not in self.global_routing_table[stack[i]]:
                    self.global_routing_table[stack[i]].append({dest_ip: stack[i - 1]})

    def LS(self):
        '''
        根据全局拓扑图 global_topo生成全局路由表
        '''
        for ip in self.global_topo.keys():
            self.global_routing_table[ip] = []
        for source_ip in self.global_topo.keys():
            for dest_ip in self.global_topo.keys():
                if source_ip != dest_ip:
                    self.Dijkstra(source_ip, dest_ip)

    # TODO: 接收各个路由器的link_table生成全局拓扑图global_topo

    # TODO: 将生成的全局路由表发往各个路由器

    # TODO: 周期检测路由器是否在线，若有路由器offline则重新生成全局路由表


# TODO: 中心化路由器
class RouterLS(Router):
    def __init__(self, send_port, recv_port, link_table):
        Router.__init__(self, send_port, recv_port, link_table)

    # TODO: 接收来自CenterServer的路由表

    # TODO: 向CenterServer发送link_table

    # TODO: 接收分组并转发


if __name__ == "__main__":
    '''
    测试LS算法
    '''
    center = CenterServer(111, 111)
    global_topo = {
        'a': [[6, 'b'], [3, 'c']],
        'b': [[6, 'a'], [2, 'c'], [5, 'd']],
        'c': [[3, 'a'], [2, 'b'], [3, 'd'], [4, 'e']],
        'd': [[5, 'b'], [3, 'c'], [2, 'e'], [3, 'f']],
        'e': [[4, 'c'], [2, 'd'], [5, 'f']],
        'f': [[3, 'd'], [5, 'e']]
    }
    center.global_topo = global_topo
    center.LS()
    for key, value in center.global_routing_table.items():
        print(key, '路由器:', value)
