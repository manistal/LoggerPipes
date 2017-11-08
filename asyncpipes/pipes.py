
import threading
import sys
import os

class AsyncPipe(threading.Thread):
    """
    Async redirection that emulates a system pipe
    Constructed from any callable that consumes a string
    """

    def __init__(self, string_consumer):

        # Set up writer redirection
        self.consume = string_consumer

        # Emulate a thread so we don't block IO 
        threading.Thread.__init__(self)
        self.daemon = False
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.start()

    # Pipe Emulation
    def fileno(self):
        return self.fdWrite

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.consume(line.rstrip())

    def run(self):
        for line in iter(self.pipeReader.readline, ''):
            self.consume(line.rstrip())
        self.pipeReader.close()

    def close(self):
        os.close(self.fileno())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


