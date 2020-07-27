import socket
import time
import os
import SocketServer
import json
import shutil
import sys
import sqlite3 as sql
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir,sep
import cgi
import hashlib
import random
import threading
#supernode = False
#node = True

from src.supernode import *
from src.node import *

def main():

    supernode = SuperNode()
    supernode.startServer()
    print "Supernode started"
    node = Node()
    #node.searchFile('Me')
    node.indexFilelist('/home/saiaravindbv/Music')
    print "HELLO"

    #downloader = Downloader()
    #downloader.download_file([('127.0.0.1',8000)],1142,'3b99153e85335ffcdb59227394e1a45d','tweets_structure1.pyc')

    # downloader = Downloader()
    # downloader.download_file([('127.0.0.1',8000)],1142,'3b99153e85335ffcdb59227394e1a45d','tweets_structure1.pyc')

    #downloader.download_file([('10.102.38.135',8000)],3990662,'f393ee6b686cad10f2c5a8bbb5eedd78','Love Me Like You Do.mp3')
    #node.download_file(ips,filesize,md5sum,filename)

if __name__ == "__main__":
    main()
