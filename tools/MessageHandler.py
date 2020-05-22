class MessageHandler:
    def handleMsg(self, msg, conn):
        # If msg equals Q break loop and listen for new connection
        if "=" in msg:
            cmd = msg.split("=")[1]
            if cmd == 'q' or cmd == 'Q':
                print("Client has closed the connection")
                conn.close()
                return ""
            else:
                return msg

        # Client Heartbeat received
        elif "con-h 0x00" in msg:
            print(f"Client heartbeat {msg}")
            return ""

        # Client has accepted timeout
        elif "con-res 0xFF" in msg:
            print(f"{msg}\nClient has accepted time out")
            conn.close()
            return ""
