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

class MyTCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True
    
# Request Handler Class
class MyTCPSuperNodeHandler(SocketServer.BaseRequestHandler):
    # def __init__(self,a,b,c):
    #     super(MyTCPSuperNodeHandler,self).__init__(a,b,c)
    #     print "Hello"
    #     self.initDB()
    #     self.childNodes = []
    #     self.otherSuperNodes = []
    otherSuperNodes = []
    nodes=[]
    nodeTimestamp = []
    lastSuperNodeUpdateTimestamp = None
    lastCreatedSuperNode = None
    chatMessage = []
    chatMessageTimestamp = []
    f=open("IP",'r')
    for i in f:
        otherSuperNodes.append(i[:-1])
    f.close()

    def handle(self):
        try:
            size=int(self.request.recv(4))
            data = json.loads(self.request.recv(size).strip())
            print data
            #data = json.loads(self.request.recv(1024).strip())
            if data['type'] == 'nSearch':
                result = self.nSearch(data['data']) 
                res = {'result':'OK','data':result}               
                msg_size=sys.getsizeof(json.dumps(res))
                self.request.send(str(msg_size))
                print msg_size
                time.sleep(1)
                print json.dumps(res)
                print "ASDASDASD"
                self.request.sendall(json.dumps(res))
            elif data['type'] == 'snSearch':
                result = self.snSearch(data['data'])
                msg_size=sys.getsizeof(json.dumps(result))
                self.request.send(str(msg_size))
                time.sleep(1)
                self.request.sendall(json.dumps(result))
            elif data['type'] == 'filelist':
                self.storeFileList(data['data'],self.client_address[0])
                result={'result':'Filelist Data'}
                msg_size=sys.getsizeof(json.dumps(result))
                self.request.send(str(msg_size))
                time.sleep(1)
                self.request.sendall(json.dumps(result))
            elif data['type'] == 'makeChild':
                done = self.addNode(self.client_address[0])
                result={'result':done}
                msg_size=sys.getsizeof(json.dumps(result))
                self.request.send(str(msg_size))
                time.sleep(1)
                self.request.send(json.dumps(result))
            elif data['type'] == 'PING':
                done = self.updateTimestamp(self.client_address[0])
                result={'result':done}
                msg_size=sys.getsizeof(json.dumps(result))
                self.request.send(str(msg_size))
                time.sleep(1)
                self.request.sendall(json.dumps(result))
            elif data['type'] == 'makeNewSuperNode':
                if self.lastSuperNodeUpdateTimestamp and self.lastSuperNodeUpdateTimestamp < 900:                    
                    result={'result':False,'data':self.lastCreatedSuperNode}
                    msg_size=sys.getsizeof(json.dumps(result))
                    self.request.send(str(msg_size))
                    time.sleep(1)
                    self.request.sendall(json.dumps(result))
            

                else:
                    for t in self.otherSuperNodes[1:]:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((t, 10000))
                        result={"type":"newSuperNode","data":self.client_address[0]}
                        msg_size=sys.getsizeof(json.dumps(result))
                        s.send(str(msg_size))
                        time.sleep(1)
                        s.sendall(json.dumps(result))
                        size=int(s.recv(4))
                        result = json.loads(s.recv(size))
                        s.close()
                    self.otherSuperNodes.append(self.client_address[0])    
                    result = {'result':True,"data":self.client_address[0]} 
                    msg_size=sys.getsizeof(json.dumps(result))
                    self.request.send(str(msg_size))
                    time.sleep(1)
                    self.request.sendall(json.dumps(result))                    
                    self.lastSuperNodeUpdateTimestamp = int(round(time.time()))
                    self.lastCreatedSuperNode = self.client_address[0]
                    print "makenodeee"
                    print self.otherSuperNodes

            elif data['type'] == 'Supernodelist':
                result = {'result':self.otherSuperNodes} 
                msg_size=sys.getsizeof(json.dumps(result))
                self.request.send(str(msg_size))
                time.sleep(1)
                self.request.sendall(json.dumps(result))

            elif data['type'] == 'newSuperNode':
                self.otherSuperNodes.append(data['data'])
                result = {'result':'OK'} 
                msg_size=sys.getsizeof(json.dumps(result))
                self.request.send(str(msg_size))
                time.sleep(1)
                self.request.sendall(json.dumps(result))
            elif data['type']=='nChat':
                timestamp = int(round(time.time())*1000);
                address = self.client_address[0]
                if address == '127.0.0.1':
                    address = self.otherSuperNodes[0]
                msg = {'message':data['data'],'timestamp':timestamp,'ip':address}
                self.chatMessage.append(msg)
                self.chatMessageTimestamp.append(timestamp)
                for t in self.otherSuperNodes[1:]:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((t, 10000))
                    result={"type":"snChat","data":msg}
                    msg_size=sys.getsizeof(json.dumps(result))
                    s.send(str(msg_size))
                    time.sleep(1)
                    s.sendall(json.dumps(result))
                    size = int(s.recv(4))
                    result = json.loads(s.recv(size))
                    s.close()
                result = {'result':'OK'} 
                msg_size=sys.getsizeof(json.dumps(result))
                self.request.send(str(msg_size))
                time.sleep(1)
                self.request.sendall(json.dumps(result))
            elif data['type'] == 'snChat':
                timestamp = int(round(time.time())*1000);
                msg = data['data']
                msg['timestamp'] = timestamp
                self.chatMessage.append(msg)
                self.chatMessageTimestamp.append(timestamp)
                result = {'result':'OK'} 
                msg_size=sys.getsizeof(json.dumps(result))
                self.request.send(str(msg_size))
                time.sleep(1)
                self.request.sendall(json.dumps(result))
            elif data['type'] == 'getChat':
                result = {'result':self.chatMessage}
                msg_size=sys.getsizeof(json.dumps(result))
                self.request.send(str(msg_size))
                time.sleep(1)
                self.request.sendall(json.dumps(result))
            else:
                result={'result':'Invalid Data'}
                msg_size=sys.getsizeof(json.dumps(result))
                self.request.send(str(msg_size))
                time.sleep(1)
                self.request.sendall(json.dumps(result))
        except Exception, e:
            print "Exception while1 receiving message: ", e
            
    # store incoming file list data
    def storeFileList(self,data,ip):
        con = None
        success = False
        dataTuples = []
        if ip == "127.0.0.1":
            ip = self.otherSuperNodes[0]
        for d in data:
            dataTuples.append((ip,d['md5sum'],d['filename'],d['size']))
        try:
            con = sql.connect('src/test.db')
            cur = con.cursor()
            cur.execute('''DELETE FROM childfiles WHERE ip = ?''',(str(ip),))
            cur.executemany('''INSERT INTO childfiles(ip,md5sum,filename,size) VALUES(?,?,?,?)''',dataTuples)
            con.commit()
            success = True
        finally:
            if con:
                con.close()
        return success

    # return super node search queries
    def snSearch(self,term):
        con = None
        rows = []
        try:
            con = sql.connect('src/test.db')
            cur = con.cursor()
            cur.execute('''SELECT ip,md5sum,filename,size FROM childfiles WHERE filename LIKE ?''',('%'+term+'%',))
            r = cur.fetchall()
            for i in r:
                rows.append({'ip':i[0],'md5sum':i[1],'filename':i[2],'size':i[3]})
        finally:
            if con:
                con.close()
        return rows

    # return node search queries
    def nSearch(self,term):
        rows = self.snSearch(term)
        for supernode in self.otherSuperNodes[1:]:
            try:
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.connect((supernode,10000))
                d = json.dumps({'type':'snSearch','data':term})
                size = sys.getsizeof(d)
                s.send(str(size))
                time.sleep(1)
                s.send(d)
                size = int(s.recv(4))
                result = json.loads(s.recv(size))
                rows.extend(result)
            finally:
                if s:
                    s.close()
        return rows

    def remove_node_files(self,ip):
        try:
            con = sql.connect('src/test.db')
            cur = con.cursor()
            cur.execute('''DELETE from childfiles WHERE ip=?''',(ip,))
            con.commit()            
        finally:
            if con:
                con.close()

    # add node
    def addNode(self,ip):
        if ip in self.nodes:
            return True
        if len(self.nodes)<2:
            self.nodes.append(ip)
            self.nodeTimestamp.append(int(round(time.time() * 1000)))
            return True
        else:
            timestamp=int(round(time.time() * 1000))
            for t in self.nodeTimestamp:
                if timestamp-t>600000:
                    self.nodes[self.nodeTimestamp.index(t)]=ip
                    self.remove_node_files(ip)
                    return True
            return False

    def updateTimestamp(self,ip):
        self.nodeTimestamp[self.nodes.index(ip)] = int(round(time.time() * 1000))
        return True

    def flushChatMessages(self):
        threading.Timer(300.0, self.flushChatMessages).start()
        timestamp = int(round(time.time())*1000)
        for t in self.chatMessage:
            if timestamp-t[1]>300000:
                if t in self.chatMessage:
                    self.chatMessage.remove(t)

class TCPNodeFileServerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            print self.client_address[0], 'connected.'
            request = self.receive()
            self.process(request)            
        except Exception, e:
            print "Exception wile receiving message: ", e
            
    def process(self, request):
        pass
        if request['type'] == 'filerequest':
            self.send_file(request['data'])
            print 'Sent.'

    def receive(self):
        request = json.loads(self.request.recv(1024))
        print 'RECEIVE:', request
        return request
    
    def send_file(self, request):
        md5sum = request['md5sum']
        offset = request['offset']
        nbytes = request['nbytes']
        filepath = None
        con = None
        try:
            con = sql.connect('src/node.db')
            cur = con.cursor()
            cur.execute('SELECT filepath FROM files WHERE md5sum = ?',(md5sum,))
            filepath = cur.fetchone()[0]
        except Exception,e:
            print e
            return
        BLOCK_SIZE = 1024
        print 'SEND:', filepath
        
        f = open(filepath, 'r')
        
        f.seek(offset)
        size = min(BLOCK_SIZE, nbytes)
        nbytes -= size
        data = f.read(size)
        while data:
            self.request.send(data)
            size = min(BLOCK_SIZE, nbytes)
            data = f.read(size)
            nbytes -= size
        f.close()
