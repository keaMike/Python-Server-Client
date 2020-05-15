import threading
import time


class ToleranceHandler:
    def __init__(self):
        self.run = True
        self.tolerance = 4
        self.toleranceCounter = 0
        self.isToleranceHit = False
        self.isMsgReceived = False
        self.conn = None

    def start(self, conn):
        self.conn = conn
        self.run = True
        toleranceThread = threading.Thread(target=self.runToleranceCounter)
        toleranceThread.start()

    def stop(self):
        self.run = False

    def runToleranceCounter(self):
        while self.run:
            if self.isToleranceHit:
                try:
                    print("Time out message send")
                    self.conn.send("con-res 0xFE".encode())
                    self.isToleranceHit = False
                except ConnectionResetError:
                    exit()
            # If a message have been received, start counting
            if self.isMsgReceived:
                # Is the tolerance counter at 4 seconds, set tolerance hit to True and send timeout
                if self.toleranceCounter == 4:
                    self.isToleranceHit = True
                time.sleep(1)
                self.toleranceCounter += 1

    def resetToleranceCounter(self):
        self.toleranceCounter = 0

    def setMsgReceived(self, state):
        self.isMsgReceived = state
