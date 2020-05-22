class SequenceHandler:
    def __init__(self):
        self.seqNum = 0

    def incrementSeqNum(self):
        self.seqNum += 1

    def validSeqNum(self, msg):
        return self.seqNum - int(self.extractSeqNum(msg)) == 0

    def extractSeqNum(self, msg):
        return msg.split("=")[0].split("-")[1]

    def getSeqNum(self):
        return self.seqNum

    def resetSeq(self):
        self.seqNum = 0
