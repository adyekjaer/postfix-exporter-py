import time
import os

class FileTailer:
    def __init__(self, filepath, parser):
        self.filepath = filepath
        self.parser = parser

    def tail(self):
        f = open(self.filepath, 'r')
        f.seek(0, 2)  # Go to end of file
        last_inode = os.fstat(f.fileno()).st_ino
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                try:
                    # Check if file has been rotated
                    current_inode = os.stat(self.filepath).st_ino
                    if current_inode != last_inode:
                        f.close()
                        f = open(self.filepath, 'r')
                        last_inode = current_inode
                        f.seek(0, 2)  # Go to end of new file
                except FileNotFoundError:
                    # File might not exist yet after rotation
                    time.sleep(0.5)
                continue
            self.parser.parse(line)
