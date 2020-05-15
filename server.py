from tools.ConfigHandler import ConfigHandler
from tools.LogHandler import LogHandler
from tools.MessageHandler import MessageHandler
from tools.PacketHandler import PacketHandler
from tools.ProtocolHandler import ProtocolHandler
from tools.SequenceHandler import SequenceHandler
from tools.SocketHandler import SocketHandler
from tools.ToleranceHandler import ToleranceHandler

# Handlers
configHandler = ConfigHandler()
logHandler = LogHandler()

seqHandler = SequenceHandler()
packetHandler = PacketHandler()
toleranceHandler = ToleranceHandler()
msgHandler = MessageHandler()
protocolHandler = ProtocolHandler()

socketHandler = SocketHandler(seqHandler, packetHandler, toleranceHandler, msgHandler, protocolHandler)


def runServer():
    socketHandler.initServer()


# Run server
runServer()
