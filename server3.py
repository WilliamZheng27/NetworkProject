import struct
import socket
import sys
import os

kilobytes = 1024
megabytes = kilobytes*1000
chunksize = int(200*megabytes)#default chunksize

def split(fromfile,todir,chunksize=chunksize):
    if not os.path.exists(todir):#check whether todir exists or not
        os.mkdir(todir)
    else:
        for fname in os.listdir(todir):
            os.remove(os.path.join(todir,fname))
    partnum = 0
    inputfile = open(fromfile,'rb')#open the fromfile
    while True:
        chunk = inputfile.read(chunksize)
        if not chunk:             #check the chunk is empty
            break
        partnum += 1
        filename = os.path.join(todir,('part%04d'%partnum))
        fileobj = open(filename,'wb')#make partfile
        fileobj.write(chunk)         #write data into partfile
        fileobj.close()
    return partnum



if __name__=='__main__':
        fromfile  = 'test.txt'
        add = "C:\ s3"
        add.replace(' ','')
        todir     = add
        chunksize = 8
        absfrom,absto = map(os.path.abspath,[fromfile,todir])
        print('Splitting',absfrom,'to',absto,'by',chunksize)
        try:
            parts = split(fromfile,todir,chunksize)
        except:
            print('Error during split:')
            print(sys.exc_info()[0],sys.exc_info()[1])
        else:
            print('split finished:',parts,'parts are in',absto)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 8258))
server.listen(1)
print("Waiting for client's request...")

while True:
    connection, addr = server.accept()  #connection:套接字对象
    print("Connect IP:", addr[0], "Port:", addr[1])
    request = connection.recv(struct.calcsize('8s')).decode('utf-8')
    print("Receive", request, "request")
    if request == 'GET F':
        connection.send('part0002'.encode('utf-8'))
        connection.send(struct.pack('Q', os.stat('part0002').st_size))
        print("Sending", os.stat('part0002').st_size, "bytes part0002...")

        file = open('part0002', 'rb')
        sendsize = 0
        while True:
            data = file.read(2 ** 23)
            if not data:
                print('file send over')
                break

            sendsize += len(data)
            connection.send(data)
            print('Have sent', sendsize, "bytes")

    connection.close()