
import sys
import threading
import subprocess as sp
from asyncpipes.pipes import AsyncPipe

def subprocess_echo(tnum, apipe):
    sp.run([f"echo '{tnum}a' && sleep 2 && echo '{tnum}b' && sleep 2 && echo '{tnum}c'"], stdout=apipe, stderr=sp.STDOUT)

def test_asyncpipes_stdout():
    for idx in range(0,3):
        th = threading.Thread(
            target=subprocess_echo, 
            args=(idx, AsyncPipes(sys.stdout.write))
        )
        th.start()
    th.join()

if __name__ == "__main__":
    test_asyncpipes_stdout() 