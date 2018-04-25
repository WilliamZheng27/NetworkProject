import struct
import socket
import sys
import os

def recv (ip,port,sendstr): #接收文件
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))
    client.send(sendstr.encode('utf-8'))
    print("Request a file")
    while True:
        filename = client.recv(struct.calcsize('8s')).decode('utf-8')
        filesize, = struct.unpack('Q', client.recv(struct.calcsize('Q')))
        recievedsize = 0
        file = open(filename, 'wb')
        print('Start receiving', filesize, 'bytes', filename)
        while recievedsize != filesize:
            if filesize - recievedsize > 2 ** 23:
                data = client.recv(2 ** 23)
                recievedsize += len(data)
            else:
                data = client.recv(filesize - recievedsize)
                recievedsize = filesize

            file.write(data)
            print("Have received", recievedsize, "bytes")
        file.close()
        print('end receive...')
        client.close()
        break

def joinfile(fromdir, filename, todir):
    if not os.path.exists(todir):
        os.mkdir(todir)
    if not os.path.exists(fromdir):
        print('Wrong directory')
    outfile = open(os.path.join(todir, filename), 'wb')
    files = os.listdir(fromdir)  # list all the part files in the directory
    files.sort()  # sort part files to read in order
    for file in files:
        filepath = os.path.join(fromdir, file)
        infile = open(filepath, 'rb')
        data = infile.read()
        outfile.write(data)
        infile.close()
    outfile.close()


if __name__ == '__main__':
    fromdir = 'C:\ s2'  #拼接文件来源的目录
    filename = 'port.txt' #拼接后的文件名称
    todir = 'C:\ untitled' #拼接后文件存放的目录

    try:
        joinfile(fromdir, filename, todir)
    except:
        print('Error joining files:')
        print(sys.exc_info()[0], sys.exc_info()[1])

recv('127.0.0.1',8260,'GET FILE')
recv('127.0.0.1',8262,'GET F')