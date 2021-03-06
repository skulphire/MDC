import select
import queue
from socket import *
from ftplib import FTP

class serverHandle(object):
    def __init__(self, port=9130,addr="172.31.82.100"):
        #ftp
        self.ftpManage = FTP("ftp.adpscommunity.com")
        self.ftpManage.login("MDC","ADPSadmin")
        self.userDir = "ADPS-Users/"
        print("#### " + self.ftpManage.dir())
        print(self.ftpManage.dir(self.userDir))
        #tcp
        self.dataQueue = {}
        self.outputs = []
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.setblocking(0)
        try:
            self.server.bind((addr, port))
            print("port:", self.server.getsockname())
            self.inputs = [self.server]
            print("Listening...")
            self.server.listen(1)
        except Exception:
            print("Could not bind, restart server or kill process!")
            exit(0)

    def start(self):
        while self.inputs:
            print(">>>")
            readable, writable, e = select.select(self.inputs,self.outputs,self.inputs)
            for s in readable:
                if s is self.server:
                    connection, client = s.accept()
                    print("   Connected to: ", client)
                    connection.setblocking(0)
                    self.inputs.append(connection)
                    self.dataQueue[connection] = queue.Queue()
                else:
                    try:
                        data = s.recv(1024)
                    except ConnectionResetError:
                        continue
                    if data:
                        print("   %s: >%s" % (s.getpeername(),self.convertToString(data)))
                        self.dataQueue[s].put(data)
                        if s not in self.outputs:
                            self.outputs.append(s)
                    else:
                        print("   Closing client with no data: ",client)
                        if s in self.outputs:
                            self.outputs.remove(s)
                        self.inputs.remove(s)
                        s.close()
                        del self.dataQueue[s]

            for s in writable:
                try:
                    nextMsg = self.dataQueue[s].get_nowait()
                except queue.Empty:
                    #print("   Output queue Is empty for: ",s.getpeername())
                    self.outputs.remove(s)
                else:
                    print("   Sending: (%s) to %s" % (self.convertToString(nextMsg),s.getpeername()))
                    s.send(nextMsg)

            for s in e:
                print("   Handling exception for: ",s.getpeername())
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
                del self.dataQueue[s]

    def convertToString(self,bite):
        str = bite.decode("utf-8")
        return str
    def checkIfLoggedIn(self, data):
        print("#### "+self.ftpManage.dir())
        print(self.ftpManage.dir(self.userDir))
        return True