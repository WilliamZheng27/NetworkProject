class Router:
    def __init__(self,router_id,router_routingTable):
        self.id = router_id
        self.routingTable = router_routingTable
    def add(self,router_new):
        self.routingTable += router_new
        self.renew()
    #TODO:刷新路由表
    def renew(self):
        #some code
    #TODO:断开路由
    def disconnect(self):
        #some code




