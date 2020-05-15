from tools.LogHandler import LogHandler

logHandler = LogHandler()


class ProtocolHandler:
    def threeWayHandshake(self, conn, ip):
        # Received client SYN
        syn = conn.recv(2048).decode()
        if self.checkProtocol(syn, "com-0"):
            print("Received SYN\n" + syn)

            # Write to log
            logHandler.write_to_file(syn)

            # Sending SYN/ACK
            print("Sending SYN/ACK...")
            conn.send(f"com-0 accept {ip}".encode())

            # Received client ACK
            ack = conn.recv(2048).decode()
            if 'accept' in ack and self.checkProtocol(ack, "com-0"):
                print("Received ACK\n" + ack)

                # Write to log
                logHandler.write_to_file(ack)

                conn.send("You are now connected".encode())
                return True
            else:
                conn.send("You are not connected... Handshake failed".encode())
                return False
        else:
            conn.send("You are not connected... Handshake failed".encode())
            return False

    def checkProtocol(self, msg, protocol):
        return msg.split(" ")[0] == protocol
