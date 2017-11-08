
import os
import sys
import threading
import subprocess as sp
from unittest import TestCase

from asyncpipes.pipes import AsyncPipe

class TestSubprocessEcho(TestCase):

    def subprocess_echo(self, tnum, apipe):
        sp.run([f"echo '{tnum}a' && sleep 2 && echo '{tnum}b' && sleep 2 && echo '{tnum}c'"], stdout=apipe, stderr=sp.STDOUT, shell=True)

    def test_asyncpipes_stdout(self):
        for idx in range(0,3):
            apipe = AsyncPipe(sys.stdout.write)
            th = threading.Thread(target=self.subprocess_echo, args=(idx, apipe))
            th.start()
