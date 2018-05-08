# -*- coding:utf-8 -*-
import Network
import socket
import json

Method_Route_Msg = '0'
Method_Data_Pack = '1'
Method_Request_Route = '2'
Method_Topo_Msg = '3'
Method_Exit_Msg = '4'


class Router:
    def __init__(self, send_port, recv_port, link_table, router_routing_table=None):
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


class RouterDV(Router):
    def __init__(self, send_port, recv_port, link_table, router_routing_table=None):
        Router.__init__(self, send_port, recv_port, link_table, router_routing_table)
        self.network_obj.start_listen(self.__msg_handler)
        for rt in self.link_table.keys():
            if link_table[rt][0]:
                try:
                    #self.network_obj.connect(rt, self.recv_port)
                    tmp_list = self.network_obj.request(rt, self.recv_port, 2, 0)
                    #self.network_obj.sock_send.settimeout(None)
                    self.routingTable[rt] = [link_table[rt][1], rt]
                    self.recv_routing_msg(tmp_list)
                except socket.error:
                    link_table[rt][0] = 0
                    continue

    # 发送本路由的路由信息
    def send_routing_msg(self, type, request_ip=''):
        print("Sending routing messages...")
        if type:
            # 逆转毒性处理
            de_possion = self.routingTable
            for key, itm in de_possion.items():
                if itm[1] == request_ip and key != itm[1]:
                    itm[0] = 9999
            self.network_obj.response(request_ip, self.send_port, 0, 0, json.dumps(de_possion))
            # 发送本机路由表
            print('Sending to ' + request_ip + '...')
            return
        for rt in self.link_table.keys():
            if self.link_table[rt][0]:
                # 逆转毒性处理
                de_possion = self.routingTable[:]
                for key,itm in de_possion.items():
                    if itm[1] == rt and key != itm[1]:
                        itm[0] = 9999
                # 发送本机路由表
                print('Sending to ' + rt + '...')
                self.network_obj.request(rt, self.recv_port, 0, 0, json.dumps(de_possion))

    def __msg_handler(self, msg):
        if msg[0] == Method_Data_Pack:
            self.routing(msg)
        elif msg[0] == Method_Route_Msg:
            self.network_obj.response(msg[1], self.send_port, 5, 0)
            self.recv_routing_msg(msg)
        elif msg[0] == Method_Request_Route:
            flag = 0
            if msg[1] in self.routingTable.keys() and self.link_table[msg[1]][1] <= self.routingTable[msg[1]][0]:
                flag = 1
                self.routingTable[msg[1]] = [self.link_table[msg[1]][1], msg[1]]
            elif msg[1] not in self.routingTable.keys():
                flag = 1
                self.routingTable[msg[1]] = [self.link_table[msg[1]][1], msg[1]]
            if flag:
                self.send_routing_msg(0)
            self.link_table[msg[1]][0] = 1
            self.send_routing_msg(1, msg[1])
        return

    # 接受其它路由的路由信息
    def recv_routing_msg(self, msg):
        dist = self.link_table[msg[1]][1]
        neibor_dict = json.loads(msg[7])
        print('Recieving routing messages from ' + msg[1] + ' ...')
        flag = 0
        for key in neibor_dict.keys():
            if key == self.network_obj.source_ip:
                continue
            elif key not in self.routingTable.keys():
                flag = 1
                self.routingTable[key] = [dist + neibor_dict[key][0], msg[1]]
            elif dist + neibor_dict[key][0] < self.routingTable[key][0]:
                flag = 1
                self.routingTable[key][0] = dist + neibor_dict[key][0]
        # 向其他路由发送更新后的路由表
        if flag:
            self.send_routing_msg(0)
        return



# TODO:LS算法、有中心服务器路由
class RouterLS(Router):
    def __init__(self, send_port, recv_port, router_routing_table=None):
        Router.__init__(self, send_port, recv_port, router_routing_table)
        self.network_obj.start_listen(self.__msg_handler)
        self.topo_table = None

    def __msg_handler(self, msg):
        if msg[0] == Method_Data_Pack:
            self.routing(msg)
        elif msg[0] == Method_Topo_Msg:
            self.recv_topo_msg(msg)
        elif msg[0] == Method_Exit_Msg:
            self.send_exit_signal()

    def recv_topo_msg(self, msg):
        return

    def send_exit_signal(self):
        return