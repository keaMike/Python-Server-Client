import threading
import time
from socket import *
from pip._vendor.distlib.compat import raw_input
from tools.ConfigHandler import ConfigHandler
from tools.LogHandler import LogHandler
from tools.ProtocolHandler import ProtocolHandler
from tools.SequenceHandler import SequenceHandler

# Handlers
logHandler = LogHandler()
configHandler = ConfigHandler()
protocolHandler = ProtocolHandler()
seqHandler = SequenceHandler()


class Client:

    # Creation of server socket. AF_INET means we're using IPv4
    # SOCK_STREAM means we're using TCP and not UDP
    def __init__(self):
        self.serverIP = '127.0.0.1'
        self.serverPort = 12000
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientIP = None
        self.isConnected = False
        self.isConfigured = False
        self.isKeepAlive = configHandler.get_config_value("opt.conf", "KeepAlive")
        self.runClient()

    def runClient(self):
        if not self.isConnected:
            # Connect to host
            self.clientSocket.connect((self.serverIP, self.serverPort))

            # Get client IP
            self.clientIP = str(self.clientSocket.getsockname()).strip(',')

            # Perform protocol handshake
            self.threeWayHandshake()

            # Check if connected
            if self.isConnected:
                # If connected start threads
                sendThread = threading.Thread(target=self.sendMsg)
                recvThread = threading.Thread(target=self.recvMsg)

                sendThread.start()
                recvThread.start()

    def threeWayHandshake(self):
        # Sending SYN packet
        syn = f"com-0 {self.clientIP}"
        print("Sending SYN...\n" + syn)
        self.clientSocket.send(syn.encode())

        # Received SYN/ACK packet
        syn_ack = self.clientSocket.recv(2048).decode()
        if 'accept' in syn_ack and protocolHandler.checkProtocol(syn_ack, "com-0"):
            print("Received SYN/ACK\nS:" + syn_ack)

            # Sending ACK packet
            ack = "com-0 accept"
            print("Sending ACK...\n" + ack)
            self.clientSocket.send(ack.encode())

            # Connection status from server
            status = self.clientSocket.recv(2048).decode()
            print(status)
            self.isConnected = True
        else:
            # Connection status from server
            status = self.clientSocket.recv(2048).decode()
            print(status)

    def sendMsg(self):
        while True:
            # If true initialize keep alive thread
            if self.isKeepAlive == 'True' and not self.isConfigured:
                print("Heartbeat initiated")
                self.isConfigured = True
                keep_alive_thread = threading.Thread(target=self.keepAliveHandler)
                keep_alive_thread.start()

            # Message from client
            time.sleep(0.5)
            sentence = raw_input("Write sentence or enter Q to exit: ")
            sentence = f"msg-{seqHandler.getSeqNum()}={sentence}"

            try:
                # Close connection if sentence is q or Q
                msg = sentence.split("=")[1]
                if msg == 'q' or msg == 'Q':
                    self.clientSocket.send(sentence.encode())
                    self.clientSocket.close()
                    exit()
                # Sending client message
                else:
                    self.clientSocket.send(sentence.encode())
                    print(f"C: {sentence}")
                    seqHandler.incrementSeqNum()
            except OSError:
                exit()

    def recvMsg(self):
        while True:
            # Receive server message
            try:
                response = self.clientSocket.recv(2048).decode()

                if seqHandler.clientValidSeqNum(response):
                    seqHandler.incrementSeqNum()
                    if "con-res 0xFE" in response:
                        self.clientSocket.send("con-res 0xFF".encode())
                        self.clientSocket.close()
                        print("\nYou have been timed out by the server")
                        exit()
                    print(f"S: {response}")
                else:
                    print("Wrong sequence number...\nClosing Connection...")
                    self.clientSocket.close()
                    self.resetClient()

            except (ConnectionResetError, ConnectionAbortedError) as e:
                print("\nConnection with host has been lost... Hit enter to exit")
                exit()

    def keepAliveHandler(self):
        while True:
            # Send heart beat packet every 3 seconds
            time.sleep(3)
            try:
                self.clientSocket.send("con-h 0x00".encode())
            except OSError:
                exit()

    def resetClient(self):
        #TODO
        pass


client = Client()
client.runClient()
