import sys
import os

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


