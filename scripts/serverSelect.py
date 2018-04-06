import select
import queue
from socket import *
from ftplib import FTP
import ftplib

class serverHandle(object):
    def __init__(self, port=9130,addr="172.31.82.100"):
        # ftp
        self.ftpManage = FTP("www.adpscommunity.com")
        self.ftpManage.login("MDC@adpscommunity.com", "ADPSadmin")
        self.ftpManage.cwd("MDC")
        self.userDir = "ADPS-Users/"
        self.areUsersLoggedIn = {}
        try:
            self.ftpManage.cwd(self.userDir)
            self.validUsers = self.ftpManage.nlst()
            for user in self.validUsers:
                self.areUsersLoggedIn[user] = False
            self.ftpManage.cwd("../")
        except Exception:
            print("No files in this directory")
            self.ftpManage.cwd("../")

        self.clients = {}
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
                        print("##"+self.convertToString(data))
                        b, user = self.checkIfLoggedIn(data, client)
                        if(b and not user == "Login"):
                            username = user.split(".")
                            self.clients[client] = username[0]
                            print("Logged in")
                            print("   %s: %s" % (self.clients[client], self.convertToString(data)))
                            if s not in self.outputs:
                                self.outputs.append(s)
                        elif b:
                            print("Already logged on")
                            print("   %s: %s" % (self.clients[client], self.convertToString(data)))
                            if s not in self.outputs:
                                self.outputs.append(s)
                        else:
                            print("Cannot allow client")
                            self.closingClient(s,"Client not allowed")

                        #self.dataQueue[s].put(data)
                    else:
                        self.closingClient(s,"disconnect")

            for s in writable:
                try:
                    nextMsg = self.dataQueue[s].get_nowait()
                except queue.Empty:
                    #print("   Output queue Is empty for: ",s.getpeername())
                    self.outputs.remove(s)
                else:
                    print("   Sending: >%s< to %s" % (self.convertToString(nextMsg),s.getpeername()))
                    s.send(nextMsg)

            for s in e:
                print("   Handling exception for: ",s.getpeername())
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
                del self.dataQueue[s]

    def closingClient(self,s,message):
        print("Closing client for:"+message)
        if s in self.outputs:
            self.outputs.remove(s)
        self.inputs.remove(s)
        s.close()
        del self.dataQueue[s]

    def convertToString(self,bite):
        str = bite.decode("utf-8")
        return str
    def checkIfLoggedIn(self, data, client):
        b = False
        #Badge:000000
        try:
            s = self.convertToString(data).split(":")
            #is this a login attempt
            if(s[0].lower() == "badge"):
                for user in self.validUsers:
                    #is it a valid user
                    if s[1]+".txt" == user:
                        #if valid user set as logged in
                        self.areUsersLoggedIn[user + ".txt"] = True
                        b = True
                        break
                    else:
                        b = False
            else:
                return False, "invalid"
            return b, s[1]
        except:
            print("excepted")
            if self.areUsersLoggedIn[self.clients[client]+".txt"] == True:
                return True, "Login"
            else:
                return False, "invalid"