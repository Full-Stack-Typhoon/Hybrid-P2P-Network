import socket
import json
import time

data = {'message':'hello world!', 'test':123.4, 'test2':123.4, 'test3':123.4, 'test4':123.4,'type':'filelist','data':[{'md5sum':'qweqweqwe','filename':'qweqweqwe','size':123123123123},{'md5sum':'asdasdasd','filename':'asdasd','size':123123123123}]}

count = 0
#while (count<1000):
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 10000))
time.sleep(3)
s.send(json.dumps(data))
result = json.loads(s.recv(1024))
print result
count+=1
time.sleep(2)
s.close()

data = {'type':'nSearch','data':'asd'}
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 10000))
time.sleep(3)
s.send(json.dumps(data))
result = json.loads(s.recv(1024))
print result
count+=1
time.sleep(2)
s.close()



