from collections import namedtuple
import socket
import time
import os
import SocketServer
import json
import shutil
import sys
import sqlite3 as sql
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
#from src.node import Downloader
from os import curdir,sep
import cgi
import hashlib
import random
import threading

class LocalHTTPServer(HTTPServer):
	def __init__(self, server_address, RequestHandlerClass):
		HTTPServer.__init__(self, server_address, RequestHandlerClass)
		self.node = None
		print "local http server class __init__"

class LocalHTTPHandler(BaseHTTPRequestHandler):
		# def __init__(self, request, client_address, server):
	# 	BaseHTTPRequestHandler.__init__(self, request, client_address, server)
		#         print "local http request handler __init__"

	def do_GET(self):
		if self.path=="/":
			self.path="/ui/index.html"

		try:
			#Check the file extension required and
			#set the right mime type

                        isdata = False

			sendReply = False
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			elif self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			elif self.path.endswith(".gif"):
				mimetype='image/gif'
				sendReply = True
			elif self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			elif self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True
                        elif self.path.endswith(".woff2"):
                                mimetype='application/font-woff2'
                                sendReply = True
                        elif self.path.endswith(".woff"):
                                mimetype='application/font-woff'
                                sendReply = True
                        elif self.path.endswith(".ttf"):
                                mimetype='application/font-ttf'
                                sendReply = True
                        elif self.path.endswith(".mp3"):
                                mimetype='audio/mpeg'
                                sendReply=True

			if sendReply == True:
				#Open the static file requested and send it
                                if isdata:
                                        f = open(curdir + sep + self.path)
                                else:
                                        f = open(curdir + sep + self.path)
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
				return
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	def do_POST(self):
		if self.path=="/uihandler":
			form = cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
						 'CONTENT_TYPE':self.headers['Content-Type'],
				})

#			print "Your name is: %s" % form["your_name"].value
			self.send_response(200)
			self.end_headers()
			print form['type']
			if form['type'].value == 'search':
					print "sent to node for search: " + form['data'].value
					searchresult = self.server.node.searchFile(form['data'].value)
#                                        print "recieved search result: " + searchresult
					json.dump(searchresult, self.wfile)

			elif form['type'].value == 'get_file':
                                print form['data'].value
				fileselected = json.loads(form['data'].value)
				ips = [ (ip, 8000) for ip in fileselected['ips'] ]
                                print ips
                                self.server.node.downloader.download_file(ips,fileselected['file']['size'], fileselected['file']['md5sum'], fileselected['file']['filename'])
                                json.dump({ 'f': str("data/"+fileselected['file']['filename'])}, self.wfile)
			elif form['type'].value == 'send_chat':
				self.server.node.send_chat(form['data'].value)

			elif form['type'].value == 'receive_chat':
				chats = self.server.node.receive_chat()
                                print "recieved chats: ", chats

                                MsgKey = namedtuple("MsgKey", ["msg", "ip"])
                                sets={}
                                for chat in chats['result']:
                                        key = MsgKey(chat['message'],chat['ip'])
                                        sets[key] = chat
                                chats = [ value for value in sets.values() ]
                                print "filtered chats: ", chats

				json.dump(chats,self.wfile)

                        elif form['type'].value == 'set_dir':
                            path = form['data'].value
                            print(path)
                            self.server.node.indexFilelist(path)

			return
