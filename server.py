import threading
import time
from socket import *

# Server port
from tools.ConfigHandler import ConfigHandler
from tools.LogHandler import LogHandler

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
log_handler = LogHandler()
msg_recv = False
is_tolerance_hit = False
is_overloaded = False
is_connected = False
tolerance_counter = 0
packet_counter = 0


def three_way_handshake():
    syn = connectionSocket.recv(2048).decode()
    if log_handler.check_protocol(syn):
        # Received client SYN
        print("Received SYN\n" + syn)

        # Sending SYN/ACK
        print("Sending SYN/ACK...")
        connectionSocket.send(f"S: con-0 accept {serverSocket.getsockname()}".encode())

        # Received client ACK
        ack = connectionSocket.recv(2048).decode()
        if 'accept' in ack and log_handler.check_protocol(ack):
            print("Received ACK\n" + ack)
            connectionSocket.send("S: You are now connected".encode())
            return True
        else:
            connectionSocket.send("S: You are not connected... Handshake failed".encode())
            return False
    else:
        connectionSocket.send("S: You are not connected... Handshake failed".encode())
        return False


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
        # Three way handshake
        status = three_way_handshake()
        if status:
            is_connected = True
            print("Accepted connection from: " + str(connectionAddress))

        while is_connected:
            # Receive message and print
            msg_sentence = connectionSocket.recv(1024).decode()
            packet_counter += 1
            msg_recv = True
            tolerance_counter = 0
            if is_overloaded:
                print("Socket overloaded... Closing client connection")
                connectionSocket.close()
                is_connected = False
            # If msg equals Q break loop and listen for new connection
            if 'q' in msg_sentence or 'Q' in msg_sentence:
                print("Client address: " + str(connectionAddress) + " have closed the connection")
                connectionSocket.close()
                is_connected = False
                break
            elif "con-h 0x00" in msg_sentence:
                print("Client heartbeat " + msg_sentence)
            # Client has accepted timeout
            elif "con-res 0xFF" in msg_sentence:
                print("Client has accepted time out")
                connectionSocket.close()
                is_connected = False
            else:
                print(f"Message from client: {msg_sentence}")
                msg_counter += 1
                connectionSocket.send(("S: res-" + str(msg_counter) + "=I AM GROOT").encode())
                msg_counter += 1


# All Threads
timeout_thread = threading.Thread(target=timeout_handler)
data_thread = threading.Thread(target=data_handler)
packet_thread = threading.Thread(target=packet_handler)

timeout_thread.start()
data_thread.start()
packet_thread.start()
