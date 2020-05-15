from socket import *


class SocketHandler:
    def __init__(self, seqHandler, packetHandler, toleranceHandler, msgHandler, protocolHandler):
        # Handlers
        self.seqHandler = seqHandler
        self.packetHandler = packetHandler
        self.toleranceHandler = toleranceHandler
        self.msgHandler = msgHandler
        self.protocolHandler = protocolHandler

        # IP and Port Number
        self.serverIP = '127.0.0.1'
        self.serverPort = 12000

        self.connectionSocket = None
        self.connectionAddress = None

        self.isRunning = True

    def initServer(self):
        # Creation of server socket. AF_INET means we're using IPv4
        # SOCK_STREAM means we're using TCP and not UDP
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((self.serverIP, self.serverPort))

        # 5 refers to amount of clients in queue
        serverSocket.listen(5)

        while True:
            print("Waiting for clients to connect...")
            self.connectionSocket, self.connectionAddress = serverSocket.accept()

            # When client accepted, start receiving messages
            self.recvMessage()

    def sendMessage(self):
        self.connectionSocket.send(f"res-{self.seqHandler.getSeqNum()}=I AM SERVER".encode())

        # Increment Sequence number
        self.seqHandler.incrementSeqNum()

    def recvMessage(self):
        # Initiate protocol handshake
        self.isRunning = self.protocolHandler.threeWayHandshake(self.connectionSocket, self.serverIP)

        # Start running packet counter
        self.packetHandler.start()

        # Start running tolerance counter
        self.toleranceHandler.start(self.connectionSocket)

        while self.isRunning:
            try:
                # Receive message and print
                msg = self.connectionSocket.recv(2048).decode()

                # Set message received to True
                self.toleranceHandler.setMsgReceived(True)

                # Increment packet counter, set message received to True and reset tolerance counter
                self.packetHandler.incrementPacketCount()

                # Reset tolerance counter
                self.toleranceHandler.resetToleranceCounter()

                # Is the server overloaded (Packet counter exceed config amount) then close connection
                if self.packetHandler.isOverloaded:
                    print("Socket overloaded... Closing client connection")
                    self.connectionSocket.close()
                    self.resetConnection()

                # Handle message
                msg = self.msgHandler.handleMsg(msg, self.connectionSocket)

                # Check if msg is empty
                if msg:
                    # If sequence number is valid (one higher than last send message)
                    if self.seqHandler.serverValidSeqNum(msg):

                        # Increment Sequence number
                        self.seqHandler.incrementSeqNum()

                        # Send message
                        self.sendMessage()
                    else:
                        print("Wrong seq num... Closing connection")
                        self.resetConnection()
                else:
                    pass
            except (OSError, ConnectionResetError) as e:
                self.resetConnection()

    def resetConnection(self):
        self.isRunning = False

        # Stop threads
        self.toleranceHandler.stop()
        self.packetHandler.stop()

        # Set message received to False
        self.toleranceHandler.setMsgReceived(False)

        # Set sequence number back to 0
        self.seqHandler.resetSeq()

        self.connectionSocket.close()
