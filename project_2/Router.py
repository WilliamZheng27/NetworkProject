#-*- coding:utf-8 -*-

import Network


class Router:
    def __init__(self,router_id,send_port,recv_port,router_routingTable=None):
        self.id = router_id
        self.routingTable = router_routingTable
        self.network_obj = Network.Network(send_port,recv_port)


    def initialize(self, method = 0):


    #TODO:刷新路由表
    '''
    Method=0:LS算法
    Method=1:DV算法
    '''
    def renew(self, neighbors,  method=0):

        if method:
            self.LS(neighbors, route_table_dict)
        return
    #TODO:断开路由
    def disconnect(self):
        return
    #TODO:转发数据包
    def routing(self, pkg):
        return
    #TODO:LS算法
    def LS(self, neighbor_distance_dict, route_table_dict):
        '''
        :param neighbor_distance_dict:字典结构，key为邻居router_id, value为距离
        :param route_table_dict:字典结构，key为邻居router_id, value为字典{key为目的router_id, value为链路长度}
        '''
        neighbor = []
        for key in neighbor_distance_dict:
            neighbor.append(key)

        self.routingTable[neighbor[0]] = (neighbor_distance_dict[neighbor[0]], neighbor[0])
        for key, value in route_table_dict[neighbor[0]].items():
            self.routingTable[key] = (neighbor_distance_dict[neighbor[0]] + value, neighbor[0])

        for i in range(1, len(neighbor)):
            if neighbor_distance_dict[neighbor[i]] < self.routingTable[neighbor[i]][0]:
                self.routingTable[neighbor[i]] = (neighbor_distance_dict[neighbor[i]], neighbor[i])
            for key, value in route_table_dict[neighbor[i]].items():
                if self.routingTable[key][0] > value + neighbor_distance_dict[neighbor[i]]:
                    self.routingTable[key] = (value + neighbor_distance_dict[neighbor[i]], neighbor[i])
#TODO:DV算法





