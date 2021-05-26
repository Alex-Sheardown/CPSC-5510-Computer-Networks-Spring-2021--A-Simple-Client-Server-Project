# Python program to implement server side of chat room.
import os
import socket
import select
import sys
import subprocess
from _thread import *


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# checks whether sufficient arguments have been provided
if len(sys.argv) != 3:
	print("Correct usage: script, IP address, port number")
	exit()


IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.bind((IP_address, Port))
server.listen(100)
list_of_clients = []


#Process ping request and organizes message according to documentation
def processPing(url):
    
    result = ""
    
    #Try catch becase url is given by client
    #Done as subprocess in order to save terminal space
    try:
        proc = subprocess.Popen(["ping -c 20 "+ url], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        result = str(out) 
    except:
        return "error with url"

    phase_1 = False
    phase_2 = False
    phase_3 = False
    phase_4 = False
    phase_5 = False
    phase_6 = False
    phase_7 = False

    answerPart1 = " \n" + "Domain tested was: " + url + " \n"
    answerPart2 = ""
    answerPart3 = ""
    answerPart4 = ""
    answerPart5 = ""
    answerPartT = ""

    #Nested For loop that looks for key characters inorder to return wanted info
    for element in range(0, len(result)):
        if not phase_1:
            if result[element] == '-' and  result[element+1] == '-' and  result[element+2] == '-' :
                phase_1 = True
        elif not phase_2:
            if result[element] == '-' and  result[element+1] == '-' and  result[element+2] == '-' :
                phase_2 = True
        elif not phase_3:
            if result[element] == 'n':
                phase_3 = True
                #begin_Count = element + 1
                x = range(12)
                for n in x:
                    #print(n)
                    if result[(element+n+1)] == 'p':
                        #print("Number of packets transmitted: " )
                        answerPart2 = result[element+1:element+int(n)+1]
                        #print(answerPart2)
                        answerPart2 = answerPart2 + " pings were sent with " 
        elif not phase_4:
            if result[element] == ',':
                phase_4 = True
                x = range(6)
                for n in x:
                    #print(n)
                    if result[(element+n)] == 'r':
                        #print("Number of packets recieved: " )
                        answerPart3 = result[element+2:element+int(n)]
                        #print(answerPart3)
                        answerPart3 = answerPart2 + answerPart3 + " pings succeeding \n"
        elif not phase_5:
            if result[element] == ',':
                phase_5 = True
                x = range(6)
                for n in x:
                    #print(n)
                    if result[(element+n)] == '%':
                        #print("Percenatage of packet loss: " )
                        answerPart4 = result[element+2:element+int(n)]
                        #print(answerPart4)
                        answerPart4 = answerPart4 + "% of packets were lost" +" \n"
        elif not phase_6:
            if result[element] == '=':
                phase_6 = True
        elif not phase_7:
            if result[element] == '/':
                phase_7 = True
                x = range(12)
                #print("Test 1: " )
                for n in x:
                    #print(n+1)
                    if result[(element+n+1)] == '/':
                        #print("Average rtt:: " )
                        answerPart5 = result[element+1:element+int(n+1)]
                        #print(result[element+1:element+int(n+1)])
                        answerPart5 =  "The average RTT was: " + answerPart5 + " \n"

    answerPartT = answerPart1 + answerPart3 + answerPart4 + answerPart5
    print(answerPartT)
    if phase_7:
        return answerPartT
    else:
        return "URL is not valid"


def clientthread(conn, addr):
    inSession = True
    # sends a message to the client whose user object is conn
    conn.send(str.encode("Welcome to this chatroom! \nPlease enter a URL to ping!" ))
    while inSession:
        message = ''
        try:
            message = str(conn.recv(2048))
        except:
            print("Error with connection")
            inSession = False
            #Is necessary
            continue

        #Removal off addons during sending
        cleanMessage = message[2:-3]
        print(cleanMessage) 
        #Test to see if shut down command was given
        try:
            if(int(cleanMessage) == 0):
                inSession = False
                break
            if(int(cleanMessage) == -10):
                print("Ending program")
                broadcast(str.encode("0"), conn)
                os._exit(1)
        except:
            sys.stdout.write("")
        
        if not message == '':
            #Preliminary check to see if message is valid 
            if(len(cleanMessage) < 4):
                conn.send(str.encode("URL is not valid"))
                continue
            else:
                print("<" + addr[0] + "> " + "now pinging: " + cleanMessage)
                # Calls broadcast function to send message to all
                message_to_send = "<" + addr[0] + "> " + processPing(str(cleanMessage))
                conn.send(str.encode(message_to_send))
                #broadcast(message_to_send, conn)
        continue

    print("<" + addr[0] + "> " + "now closing connection " )
    remove(conn)
    conn.close()


def broadcast(message, connection):
    for clients in list_of_clients:
        if clients!=connection:
            try:
                clients.send(message)
            except:
                clients.close()
                # if the link is broken, we remove the client
                remove(clients)

def remove(connection):
	if connection in list_of_clients:
		list_of_clients.remove(connection)

mainSession = True
while mainSession:
    
    conn, addr = server.accept()
    list_of_clients.append(conn)

    # prints the address of the user that just connected
    print (addr[0] + " connected")

    # creates and individual thread for every user
    # that connects
    start_new_thread(clientthread,(conn,addr))	

conn.close()
server.close()
