import threading
import time
from socket import *

# Server port
from tools.ConfigHandler import ConfigHandler

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


# Global Attributes
config_handler = ConfigHandler()
msg_recv = False
is_tolerance_hit = False
is_overloaded = False
is_connected = False
tolerance_counter = 0
packet_counter = 0


def timeout_handler():
    global tolerance_counter
    global is_tolerance_hit

    while True:
        if is_tolerance_hit:
            try:
                print("Time out message send")
                connectionSocket.send("con-res 0xFE".encode())
                is_tolerance_hit = False
            except ConnectionResetError:
                exit()
        if msg_recv:
            if tolerance_counter == 4:
                is_tolerance_hit = True
            time.sleep(1)
            tolerance_counter += 1


def packet_handler():
    global packet_counter
    global is_overloaded

    max_packets = int(config_handler.get_config_value("opt.conf", "MaxPackets"))
    while True:
        if is_connected:
            time.sleep(1)
            print("num of packets recv: " + str(packet_counter))
            if packet_counter < max_packets:
                packet_counter = 0
            else:
                is_overloaded = True


def data_handler():
    global connectionSocket
    global connectionAddress
    global is_connected
    global tolerance_counter
    global msg_recv
    global packet_counter

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
                packet_counter += 1
                msg_recv = True
                tolerance_counter = 0
                if is_overloaded:
                    print("Socket overloaded... Closing client connection")
                    connectionSocket.close()
                    is_connected = False
                # If msg er lig Q break loop og lyt efter ny forbindelse
                if msg_sentence in ('q', 'Q'):
                    print("Client address: " + str(connectionAddress) + " have closed the connection")
                    connectionSocket.close()
                    is_connected = False
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
packet_thread = threading.Thread(target=packet_handler)

timeout_thread.start()
data_thread.start()
packet_thread.start()
