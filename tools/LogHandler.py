from datetime import datetime


class LogHandler:
    def write_to_file(self, msg):
        # Open file and set to w (write)
        file = open("log.txt", "a")
        # Date now
        now = datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        file.write(f"{dt_string} - {msg}\n")
        file.close()
