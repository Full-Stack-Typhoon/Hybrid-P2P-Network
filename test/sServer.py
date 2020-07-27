import SocketServer
import json
import sqlite3 as sql

fileList = []
nodes = []
otherSupernodes = []

class MyTCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

class MyTCPServerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            data = json.loads(self.request.recv(1024).strip())
            # process the data, i.e. print it:
            print data
            # send some 'ok' back
            self.request.sendall(json.dumps({'result':'ok'}))
        except Exception, e:
            print "Exception wile receiving message: ", e

server = MyTCPServer(('localhost', 10000), MyTCPServerHandler)
server.serve_forever()

def initDB():
    con = None
    try:
        con = sql.connect('test.db')
        cur = con.cursor()
        cur.execute('DROP TABLE IF EXIST childfiles')
        cur.execute('CREATE TABLE childfiles(ip text,md5sum text, filename text)')

    finally:
        if con:
            con.close()

def storeFileList(data):
    con = None
    try:
        con = sql.connect('test.db')
        cur = con.cursor()
        cur.execute('''DELETE FROM childfiles WHERE ip = ?''',(data.ip))
        cur.executemany('''INSERT INTO childfiles(ip,md5sum,filename) VALUES(?,?,?)''',data.filelist)
        con.commit()
    finally:
        if con:
            con.close()

def search(term):
    con = None
    try:
        con = sql.connect('test.db')
        cur = con.cursor()
        cur.execute('''SELECT * FROM childlist WHERE filename LIKE ?''','%'+term+'%')
        rows = cur.fetchall()
    finally:
        if con:
            con.close()
    return rows

def addNode(ip):
    nodes.add(ip)
