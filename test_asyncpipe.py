
import os
import sys
import threading
import subprocess as sp
from unittest import TestCase
from time import sleep

from asyncpipes.pipes import AsyncPipe

def string_pass(something):
    print("EW!", something)

def subprocess_noecho(tnum):
    with AsyncPipe(string_pass) as apipe:
        sp.run([f"echo '{tnum}a\n' && sleep 2 && echo '{tnum}b\n' && sleep 2 && echo '{tnum}c\n'"], stdout=apipe, stderr=sp.STDOUT, shell=True)

def subprocess_echo(tnum):
    with AsyncPipe(sys.stdout.write) as apipe:
        sp.run([f"echo '{tnum}a\n' && sleep 2 && echo '{tnum}b\n' && sleep 2 && echo '{tnum}c\n'"], stdout=apipe, stderr=sp.STDOUT, shell=True)

def test_asyncpipes_spstdout():
    print("SPSTDOUT START!")
    for idx in range(0,3):
        th = threading.Thread(target=subprocess_echo, args=(idx,))
        th.start()
    th.join()
    print("SPSTDOUT Done!")

def test_asyncpipes_nostdout():
    print("NO STDOUT START!")
    for idx in range(0,3):
        th = threading.Thread(target=subprocess_noecho, args=(idx,))
        th.start()
    th.join()
    print("NO STDOUT DONE! ")

if __name__ == "__main__":
    test_asyncpipes_spstdout()
    test_asyncpipes_nostdout()
