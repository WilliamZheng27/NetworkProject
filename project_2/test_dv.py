import Router
send_port = 23333
recv_port = 10086
link_table = ['192.168.199.205', '172.18.35.96']
if __name__ == '__main__':
    router_obj = Router.RouterDV(send_port,recv_port,link_table)

