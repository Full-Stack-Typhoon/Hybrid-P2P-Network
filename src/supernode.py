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
import thread
from src.server import *

class SuperNode():
    def __init__(self):
        self.server = None

        
    def startServer(self):
        self.initDB()
        print "init db server"
        server = MyTCPServer(('',10000),MyTCPSuperNodeHandler)
        try:
            thread.start_new_thread(server.serve_forever,())
        except Exception,e:
            print e

    def stopServer(self):
        server.shutdown()

    def initDB(self):
        con = None
        try:
            con = sql.connect('src/test.db')
            cur = con.cursor()
            cur.execute('DROP TABLE childfiles')
            cur.execute('CREATE TABLE childfiles(ip text,md5sum text, filename text,size int)')
        finally:
            if con:
                con.close()
