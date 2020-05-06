import threading
import time
from socket import *
from pip._vendor.distlib.compat import raw_input

# Server navn og server port
from tools.ConfigHandler import ConfigHandler
from tools.LogHandler import LogHandler

serverIP = '127.0.0.1'
serverPort = 12000
# Oprettelse af client socket. AF_INET gør at vi bruger IPv4
# SOCK_STREAM henviser til at vi anvender TCP og ikke UDP
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverIP, serverPort))
clientIP = str(clientSocket.getsockname()).strip(',')

# Global Attributes
log_handler = LogHandler()
config_handler = ConfigHandler()
is_connected = False
is_configured = False
msg_counter = 0


def three_way_handshake():
    global is_connected
    # Sending SYN packet
    syn = f"C: con-0 {clientIP}"
    print("Sending SYN...\n" + syn)
    clientSocket.send(syn.encode())

    # Received SYN/ACK packet
    syn_ack = clientSocket.recv(2048).decode()
    if 'accept' in syn_ack and log_handler.check_protocol(syn_ack):
        print("Received SYN/ACK\n" + syn_ack)

        # Sending ACK packet
        ack = "C: con-0 accept"
        print("Sending ACK...\n" + ack)
        clientSocket.send(ack.encode())

        # Connection status from server
        status = clientSocket.recv(2048).decode()
        print(status)
        is_connected = True
    else:
        # Connection status from server
        status = clientSocket.recv(2048).decode()
        print(status)


def send_msg():
    global msg_counter
    global is_configured
    while True:
        # Getting keep alive configuration
        keep_alive = config_handler.get_config_value("opt.conf", "KeepAlive")
        # If true initialize keep alive thread
        if keep_alive and not is_configured:
            print("Heartbeat initiated")
            is_configured = True
            keep_alive_thread = threading.Thread(target=keep_alive_handler)
            keep_alive_thread.start()
        # Message from client
        time.sleep(0.5)
        sentence = raw_input("Write sentence or enter Q to exit: ")
        try:
            # Close connection if sentence is q or Q
            if sentence in ('q', 'Q'):
                clientSocket.send(sentence.encode())
                clientSocket.close()
                print("Connection with the server has been closed")
                exit()
            else:
                # Sending client message
                clientSocket.send(sentence.encode())
                print("C: msg-" + str(msg_counter) + "=" + sentence)
                msg_counter += 1
        except OSError:
            exit()


def recv_msg():
    global msg_counter
    while True:
        # Receive server message
        try:
            response = clientSocket.recv(2048).decode()
            msg_counter += 1
            if response in "con-res 0xFE":
                clientSocket.send("con-res 0xFF".encode())
                clientSocket.close()
                print("\nYou have been timed out by the server")
                exit()
            print(response)
        except ConnectionAbortedError:
            exit()


def keep_alive_handler():
    global clientSocket
    while True:
        time.sleep(3)
        try:
            clientSocket.send("con-h 0x00".encode())
        except OSError:
            exit()


three_way_handshake()
if is_connected:
    send_thread = threading.Thread(target=send_msg)
    recv_thread = threading.Thread(target=recv_msg)

    send_thread.start()
    recv_thread.start()
