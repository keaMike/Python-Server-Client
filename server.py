import threading
import time
from socket import *

# Server port
serverIP = '127.0.0.1'
serverPort = 12000
# Oprettelse af server socket. AF_INET gør at vi bruger IPv4
# SOCK_STREAM henviser til at vi anvender TCP og ikke UDP
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverIP, serverPort))
# Hvor lang socket køen kan være
serverSocket.listen(1)

connectionSocket = None
connectionAddress = None

msg_recv = False
isToleranceHit = False
toleranceCounter = 0


def timeout_handler():
    global connectionSocket
    global toleranceCounter
    global isToleranceHit
    global msg_recv

    while True:
        if isToleranceHit:
            try:
                print("Time out message send")
                connectionSocket.send("con-res 0xFE".encode())
                isToleranceHit = False
            except ConnectionResetError:
                exit()
        if msg_recv:
            if toleranceCounter == 4:
                isToleranceHit = True
            time.sleep(1)
            toleranceCounter += 1
            print(toleranceCounter)


def data_handler():
    global connectionSocket
    global connectionAddress
    global toleranceCounter
    global isToleranceHit
    global msg_recv

    while True:
        msg_recv = False
        msg_counter = 0
        print("Waiting for clients to connect...")
        connectionSocket, connectionAddress = serverSocket.accept()
        is_connected = True
        # Send acceptance message
        connectionSocket.send((f"S: com-0 accept {serverSocket.getsockname()}".encode()))
        print("Accepted connection from: " + str(connectionAddress))

        while True:
            if is_connected:
                # Modtag message og print
                msg_sentence = connectionSocket.recv(1024).decode()
                msg_recv = True
                toleranceCounter = 0
                # If msg er lig Q break loop og lyt efter ny forbindelse
                if msg_sentence in ('q', 'Q'):
                    print("Client address: " + str(connectionAddress) + " have closed the connection")
                    break
                elif msg_sentence in "con-h 0x00":
                    print("Client heartbeat " + msg_sentence)
                # Client has accepted timeout
                elif msg_sentence in "con-res 0xFF":
                    print("Client has accepted time out")
                    connectionSocket.close()
                    is_connected = False
                else:
                    print(f"Message from client: {msg_sentence}")
                    msg_counter += 1
                    connectionSocket.send(("S: res-" + str(msg_counter) + "=I AM GROOT").encode())
                    msg_counter += 1
            else:
                break


timeout_thread = threading.Thread(target=timeout_handler)
data_thread = threading.Thread(target=data_handler)

timeout_thread.start()
data_thread.start()
