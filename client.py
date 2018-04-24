import struct
import socket
import sys
import os

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8255))

client.send("GET FILE".encode('utf-8'))
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



client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client1.connect(('127.0.0.1', 8258))
client1.send("GET F".encode('utf-8'))
print("Request a file")
while True:
    filename = client1.recv(struct.calcsize('8s')).decode('utf-8')
    filesize, = struct.unpack('Q', client1.recv(struct.calcsize('Q')))
    recievedsize = 0

    file = open(filename, 'wb')

    print('Start receiving', filesize, 'bytes', filename)
    while recievedsize != filesize:
        if filesize - recievedsize > 2 ** 23:
            data = client1.recv(2 ** 23)
            recievedsize += len(data)
        else:
            data = client1.recv(filesize - recievedsize)
            recievedsize = filesize

        file.write(data)
        print("Have received", recievedsize, "bytes")
    file.close()
    print('end receive...')
    client1.close()
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
    fromdir = 'C:\ s2'
    filename = 'port.txt'
    todir = 'C:\ untitled'

    try:
        joinfile(fromdir, filename, todir)
    except:
        print('Error joining files:')
        print(sys.exc_info()[0], sys.exc_info()[1])