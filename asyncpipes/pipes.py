
from datetime import datetime
import threading
import logging
import sys
import os


class LoggingPipe(threading.Thread):
    """
    Logging redirection that emulates a system pipe
    """

    def __init__(self, classname, funcname):
        self.classname = classname
        self.funcname = funcname

        # Setup a buffer/seperate logger per pipe
        self.logbuffer = "/tmp/buildwatch.%s.%s" % (os.getpid(), self.funcname)
        self.datefmt_string = "%H:%M:%S"
        self.format_string = "[{classname}][{funcname}][%(asctime)s] %(message)s".format(
            classname=self.classname, funcname=self.funcname)

        self.logger = self.make_logger()

        # Emulate a thread so we don't block IO 
        threading.Thread.__init__(self)
        self.daemon = False
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.start()

    def make_logger(self):
        # Logger factory to set up our logger in constructor
        logger = logging.getLogger(self.classname+self.funcname)
        buffer_formatter = logging.Formatter(self.format_string, self.datefmt_string)
        buffer_handler = logging.StreamHandler()

        buffer_handler.setFormatter(buffer_formatter)
        logger.addHandler(buffer_handler) 
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        return logger

    # Pipe emulation
    def fileno(self):
        return self.fdWrite

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.info(line.rstrip())

    def run(self):
        for line in iter(self.pipeReader.readline, ''):
            self.logger.info(line.rstrip())
        self.pipeReader.close()

    def close(self):
        os.close(self.fdWrite)
        sys.stdout.flush()

    # Context Handling
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info("Starting!")

        sys.stdout = self
        sys.stderr = self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        # Nice little timer functionality (cosmetic) 
        elapsed_time = str(datetime.now() - self.start_time)
        self.logger.info("Done! Elapsed %s", elapsed_time)

        self.close()

class BufferedLoggingPipe(LoggingPipe):
    """
    Buffered STDOUT Logger that emulates a Pipe 
    """
    def make_logger(self):
        # Logger factory to set up our logger in constructor
        logger = logging.getLogger(self.classname+self.funcname)
        buffer_formatter = logging.Formatter(self.format_string, self.datefmt_string)
        buffer_handler = logging.FileHandler(self.logbuffer)

        buffer_handler.setFormatter(buffer_formatter)
        logger.addHandler(buffer_handler) 
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        return logger

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        # Nice little timer functionality (cosmetic) 
        elapsed_time = str(datetime.now() - self.start_time)
        self.logger.info("Done! Elapsed %s", elapsed_time)

        # Dump everything to stdout now that its done
        with open(self.logbuffer, 'r') as logbuffer:
            for line in logbuffer.readlines():
                sys.stdout.write(line)
        os.remove(self.logbuffer)

        self.close()


class FileLoggingPipe(LoggingPipe):
    """
    Logger that uses root logfile that emulates a pipe
    """
    def make_logger(self):
        logger = logging.getLogger()
        logger.propegate = False

        for handler in logger.handlers:
            buffer_formatter = logging.Formatter(self.format_string, self.datefmt_string)
            handler.setFormatter(buffer_formatter)

        return logger


def logpipes(classfunc):
    """
    Default STDOUT redirection is a buffered stdout, designed to reduce Jenkins loads
    the argument --suppress-buffer just runs the stdout lines through a stdout logger
    the argument --suppress-output redirects stdout through a filehandle logger
    """
    def stdout(self, *args, **kwargs):
        classname = self.__class__.__name__.replace('Watcher', '')
        funcname = classfunc.__name__

        if self.cmd_args.suppress_output:
            with FileLoggingPipe(classname, funcname) as FLP:
                return classfunc(self, *args, **kwargs)

        if self.cmd_args.suppress_buffer:
            with LoggingPipe(classname, funcname) as LP:
                return classfunc(self, *args, **kwargs)

        with BufferedLoggingPipe(classname, funcname) as BLP:
            return classfunc(self, *args, **kwargs)

    return stdout


