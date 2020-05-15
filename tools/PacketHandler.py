import threading

from tools.ConfigHandler import ConfigHandler
import time

configHandler = ConfigHandler()


class PacketHandler:
    def __init__(self):
        self.run = True
        self.packetCounter = 0
        self.maxPackets = int(configHandler.get_config_value("opt.conf", "MaxPackets"))
        self.isOverloaded = False

    def start(self):
        self.run = True
        packetThread = threading.Thread(target=self.runPacketCounter)
        packetThread.start()

    def stop(self):
        self.run = False

    def runPacketCounter(self):
        while self.run:
            time.sleep(1)
            if self.packetCounter != 0:
                print("num of packets recv: " + str(self.packetCounter))
            if self.packetCounter < self.maxPackets:
                self.packetCounter = 0
            else:
                self.isOverloaded = True

    def incrementPacketCount(self):
        self.packetCounter += 1
