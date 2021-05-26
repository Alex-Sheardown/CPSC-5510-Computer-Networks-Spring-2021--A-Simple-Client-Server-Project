# Python program to implement client side of chat room.
import socket
import select
import sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Basic set up check
if len(sys.argv) != 3:
	print ("Correct usage: script, IP address, port number")
	exit()

IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))
sockets_list = [sys.stdin, server]

inSession = True

print("Enter 0 to end client or -10 to end client and Server")
while inSession:
    #only works on linux systems 
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])
    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            if len(str(message)) < 6:
                    print("Session closed")
                    inSession = False
                    server.close()
                    break

            #For when server shuts down
            try:
                if(int(message) == 0):
                    print("End Request given")
                    print("Shutting down")
                    inSession = False
                    break
            except:
                x=0
            #For when infinite loop of empty messages when server disconnects
            if(len(message) < 4):
                continue
            else:
                message = str(message).replace('\\n', '\n')
                print(str(message))
        else:
            #Collecting message
            message = sys.stdin.readline()
            server.send(str.encode(message))
            sys.stdout.write("<You>")
            sys.stdout.write(message)
            #Shutdown method for client and server
            try:
                if(int(message) == 0):
                    inSession = False
                    break
                if(int(message) == -10):
                    inSession = False
                    break
            except:
                x = 0
            sys.stdout.flush()
#For closing server
print("Session Ended")
server.close()
