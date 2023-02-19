import os
from datetime import datetime


class Logger:
    def __init__(self):
        self.file_name = "logs/" + datetime.now().strftime("%Y-%m-%dT%H_%M_%SZ") + ".txt"

    def write_to_logfile(self, text):
        print(text)
        if not os.path.exists("logs/"):
            os.mkdir("logs")
        with open(self.file_name, "a") as f:
            f.write(text + "\n")