'''
file_sha(string):整个文件的SHA1
seg_sha(list):分块的SHA1列表
    seg in seg_sha:
    seg(string):分块的SHA1
'''


class File:
    def __init__(self,file_sha,seg_sha):
        self.file_sha = file_sha
        self.seg_sha = seg_sha


#文件列表
file_list = []

#TODO:读取文件列表

#TODO：与Tracker建立连接

#TODO：与Tracker断开连接

#TODO：向Tracker请求文件

#TODO：向Tracker增加文件

#TODO：向Peer请求文件分块

#TODO:文件分割

#TODO：文件合并