import socket
import time
import os
import SocketServer
import json
import shutil
import sys
import sqlite3 as sql
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from src.http_server import *
from os import curdir,sep
import cgi
import hashlib
import random
import threading
import thread
from src.server import *
from src.supernode import *

class Downloader():
    def __init__(self):
        self.dir = "data/"
        self.filename = ""


    def request_part_file(self, (host, port), filename, md5sum, offset, nbytes, id):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print 'Connecting... ' + host + ':' + str(port) + ' Filename: ' + filename + '\tOffset: ' + str(offset) + '\t\tSize: ' + str(nbytes)
            s.connect((host, port))
            request = {
                'type': 'filerequest',
                'data': {
                    'filename': filename,
                    'offset': offset,
                    'nbytes': nbytes,
                    'md5sum': md5sum
                }
            }
            # print 'SEND:', request
            s.send(json.dumps(request))
            self.receive_file(s, offset, id)
        except:
            return False
        finally:
            s.close()
            return True

    def receive_file(self, s, offset, id):
        if offset == 0:
            f = open(self.dir + self.filename, 'w')
        else:
            f = open(self.dir + self.filename + '_' + str(id), 'w')

        BLOCK_SIZE = 1024
        response = s.recv(BLOCK_SIZE)
        while (response):
            f.write(response)
            response = s.recv(BLOCK_SIZE)
        f.close()

    def download_file(self, ips, filesize, md5sum, filename):
        print "Downloading ...", filename

        self.filename = filename
        n = 0
        offset = 0
        part_size = min(1048576, filesize)

        # download main file
        for (host, port) in ips:
            if self.request_part_file((host, port), filename, md5sum, offset, part_size, 0): break
        offset = part_size
        part_size = min(filesize - offset, part_size)
        n += 1
        time.sleep(1)

        while offset < filesize:
            for (host, port) in ips:
                try:
                    if not self.request_part_file((host, port), filename, md5sum, offset, part_size, n):
                        break
                except Exception, e:
                    print e
                    sys.exit()

            part_filename = self.dir + self.filename + '_' + str(n)
            self.append_part_file(part_filename)
            offset += part_size
            part_size = min(filesize - offset, part_size)
            time.sleep(1)
            n += 1
        print "Downloading done."
        return
        #raise Exception('Not downloaded.')

    def append_part_file(self, part_filename):
        # print "Appending ..."
        BLOCK_SIZE = 1024
        print(self.filename, '<-', part_filename)

        f = open(self.dir + self.filename, 'a')
        part_file = open(part_filename, 'r')

        data = part_file.read(BLOCK_SIZE)
        while data:
            f.write(data)
            data = part_file.read(BLOCK_SIZE)
        part_file.close()
        f.close()

        # print "Appending done."

        self.clean_part_files()

    def clean_part_files(self):
        pass

class Node():
    def __init__(self):
        thread.start_new_thread(self.startHTTPServer,())
        self.downloader = Downloader()
        #self.startHTTPServer()
        self.supernode = None
        self.supernodes = []
        f=open("IP",'r')
        for i in f:
            self.supernodes.append(i[:-1])
        f.close()
        print "supernode read"
        self.choose_supernode()
        print "supernode_chosen"
        self.check_SuperNode()
        print "checking supernode"
        self.updateSuperNodesFile()
        print "update supernode file"
        self.initDB()
        print "initdb"
        self.startFileServer()
        print "server started"
        #self.supernode = None
        #self.selectSuperNode()

    def receive_chat(self):
        result = self.sendRequest('getChat'," ")
        return result

    def send_chat(self,message):
        self.sendRequest('nChat',message)

    def choose_supernode(self):
        if len(self.supernodes) == 0:
            self.requestNewSuperNode()
        else:
            ip=self.supernodes[random.randint(0,len(self.supernodes)-1)]
            self.supernode=ip
            result=self.sendRequest("makeChild"," ")
            print result
            if result and not result['result']:
                self.updateSupernodesList(self.supernode)
                self.choose_supernode()

    def requestNewSuperNode(self):
        supernodes=[]
        f=open("IP",'r')
        for i in f:
            supernodes.append(i[:-1])
        f.close()
        for s in supernodes:
            self.supernode = s
            result = self.sendRequest("makeNewSuperNode"," ")
            if result:
                if result['result']:
                    self.supernode = result['data']
                    self.supernodes.append(result['data'])
                    f = open("IP","w")
                    f.write(result['data']+"\n")
                    for i in supernodes:
                        f.write(str(i)+"\n")
                    f.close()
                    supernode = SuperNode()
                    supernode.startServer()
                    print "SuperNode STARTED"
                    break
                else:
                    self.supernode = result['data']
                    self.supernodes.append(result['data'])
                    break

    def startHTTPServer(self):
        try:
            server = LocalHTTPServer(("localhost",8080),LocalHTTPHandler)
            server.node = self
            print "HTTP Server Starting"
            server.serve_forever()
        except Exception, e:
            print e
        finally:
            print "HTTP Server Started"

    def stopHTTPServer(self):
        try:
            server.socket.close()
        finally:
            print "HTTP Server Shutdown"

    def startFileServer(self):
        server = MyTCPServer(('',8000),TCPNodeFileServerHandler)
        try:
            thread.start_new_thread(server.serve_forever,())
        except Exception,e:
            print e

    def initDB(self):
        con = None
        try:
            con = sql.connect('src/node.db')
            cur = con.cursor()
            cur.execute('DROP TABLE files')
            cur.execute('CREATE TABLE files(filepath text,md5sum text, filename text,size text)')

        finally:
            if con:
                con.close()

    def populateDB(self,data):
        con = None
        try:
            con = sql.connect('src/node.db')
            cur = con.cursor()
            cur.executemany('''INSERT INTO files(filepath,md5sum,filename,size) VALUES(?,?,?,?)''',data)
            con.commit()

        finally:
            if con:
                con.close()

    def updateSupernodesList(self,ip):
        # f=open("IP","r")
        # lines = f.readlines()
        # f.close()
        # f=open("IP","w")
        # for line in lines:
        #   if line!=ip+"\n":
        #       f.write(line)
        # f.close()
        if ip in self.supernodes:
            self.supernodes.remove(ip)

    def updateSuperNodesFile(self):
        threading.Timer(900.0, self.updateSuperNodesFile).start()
        supernodes=[]
        f=open("IP",'r')
        for i in f:
            supernodes.append(i[:-1])
        f.close()
        for s in supernodes:
            result=self.sendRequest("Supernodelist"," ")
            if result:
                f=open("IP","w")
                for line in result['result']:
                    f.write(line+"\n")
                f.close()
                self.supernodes=result['result']
                break



    def sendRequest(self,requestType,requestData):
        jsonObject = {}
        jsonObject["type"] = requestType;
        jsonObject["data"] = requestData;
        result=False
        print jsonObject
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect((self.supernode,10000))
            msg_size=sys.getsizeof(json.dumps(jsonObject))
            s.send(str(msg_size))
            time.sleep(1)
            s.send(json.dumps(jsonObject))
            size=int(s.recv(4))
            result = json.loads(s.recv(size))
        except Exception,e:
            print "Exception wile receiving message: ", e
        finally:
            if s:
                s.close()
            return result

    def indexFilelist(self,directory):
        file_list=[]
        database=[]
        file_structure=[]
        for root, dirs, files in os.walk(directory, topdown=True):
            for name in files:
                    file_list.append(os.path.join(root, name))
        for f in file_list:
            json_object={}
            filename=f.split("/")[-1]
            md5sum=self.computeMD5SUM(f)
            json_object["md5sum"]=md5sum
            json_object["filename"]=filename
            json_object["size"]=os.path.getsize(f)
            file_structure.append(json_object)
            database.append((f,md5sum,filename,os.path.getsize(f)))
        # Populate database
        self.populateDB(database)
        self.sendRequest("filelist",file_structure)

    def computeMD5SUM(self,filename):
        f=open(filename).read()
        md5sum=hashlib.md5(f).hexdigest()
        return md5sum

    def searchFile(self,term):
        result = self.sendRequest('nSearch',term)
        print result
        return result


    def check_SuperNode(self):
        threading.Timer(300.0, self.check_SuperNode).start()
        print "Hello, World!"
        result=self.sendRequest('PING'," ")
        if not result:
            self.updateSupernodesList(self.supernode)
            self.choose_supernode()
