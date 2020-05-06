class LogHandler:
    def writeToFile(self, msg):
        #Open file and set to w (write)
        file = open("log.txt", "w")
        file.write(msg)
        file.close()
        
