import threading
import time
from socket import *
from pip._vendor.distlib.compat import raw_input

# Server navn og server port
serverIP = '127.0.0.1'
serverPort = 12000
# Oprettelse af client socket. AF_INET gør at vi bruger IPv4
# SOCK_STREAM henviser til at vi anvender TCP og ikke UDP
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverIP, serverPort))
clientIP = str(clientSocket.getsockname()).strip(',')

print("C: com-0 " + clientIP)
print(clientSocket.recv(2048).decode())
print("C: com-0 accept")
print("You are now connected to the server\n")

msg_counter = 0


def send_msg():
    global msg_counter
    while True:
        # Besked fra brugeren
        time.sleep(0.5)
        sentence = raw_input("Write sentence or enter Q to exit: ")
        try:
            if sentence in ('q', 'Q'):
                clientSocket.send(sentence.encode())
                clientSocket.close()
                print("Connection with the server has been closed")
                exit()
            else:
                # Sender brugerens besked
                clientSocket.send(sentence.encode())
                print("C: msg-" + str(msg_counter) + "=" + sentence)
                msg_counter += 1
        except OSError:
            exit()


def recv_msg():
    global msg_counter
    while True:
        # Modtager server besked
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


send_thread = threading.Thread(target=send_msg)
recv_thread = threading.Thread(target=recv_msg)
send_thread.start()
recv_thread.start()
