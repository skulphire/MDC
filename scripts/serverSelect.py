import select
import queue
import time
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
                #print("user>"+user)
                self.areUsersLoggedIn[user] = False
            self.ftpManage.cwd("../")
        except Exception:
            print("No files in this directory")
            self.ftpManage.cwd("../")


        self.clientsIP = {}
        self.clients = {}
        self.clientText = {}
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
        print(">>>")
        while self.inputs:
            readable, writable, e = select.select(self.inputs,self.outputs,self.inputs)
            for s in readable:
                if s is self.server:
                    connection, client = s.accept()
                    print("   Connected to: ", client)
                    connection.setblocking(0)
                    self.inputs.append(connection)
                    self.dataQueue[connection] = queue.Queue()
                    print(self.clients)
                else:
                    try:
                        data = s.recv(1024)
                    except Exception:
                        continue
                    if data:
                        #if not logged on, try to login
                        if s not in self.clients or self.areUsersLoggedIn[self.clients[s] + ".txt"] is False:
                            b, user = self.checkIfLoggedIn(data, s)
                        else:
                            b = False
                            user = ""
                        if(b and not user == "Login"):
                            username = user.split(".")
                            self.clients[s] = username[0]
                            self.clientText[s] = username[0]
                            self.clientsIP[username[0]] = s
                            #sending ftp login info
                            print("Logged in")
                            print("   %s: %s" % (self.clients[s], self.convertToString(data)))
                            s.send(self.convertToBytes("Valid"))
                            time.sleep(.5)
                            s.send(self.convertToBytes("FTP:MDC@adpscommunity.com:ADPSadmin"))
                            if s not in self.outputs:
                                self.outputs.append(s)
                        #if already logged on, handle data
                        elif s in self.clients and self.areUsersLoggedIn[self.clients[s] + ".txt"] is True:
                            message = self.convertToString(data)
                            #sendto:badge:message
                            if "sendto" in message.lower():
                                sending = message.split(":")
                                #sending[1] = badge
                                #sending[2] = message
                                if sending[1] in self.clientsIP:
                                    reciever = self.clientsIP[sending[1]]
                                    reciever.send(self.convertToBytes(sending[2]))
                                    s.send(self.convertToBytes("Valid"))
                                    print("valid")
                                else:
                                    s.send(self.convertToBytes("Invalid"))
                                    print("invalid")
                            #get user list
                            elif "userlist" in message.lower():
                                sending = "userlist"
                                for user in self.validUsers:
                                    t = user.split(".")
                                    user = t[0]
                                    if user is not "":
                                        sending = sending+":"+user
                                #print("   %s> %s" % ("sending to>"+self.clients[peer], sending))
                                s.send(self.convertToBytes(sending))
                            elif "desktop" in message.lower():
                                self.clientText[s]+="(Desktop)"
                            elif "gta" in message.lower():
                                self.clientText[s]+="(Game)"
                            elif "loggedinusers" in message.lower():
                                sending = "usersonline"
                                for user in self.areUsersLoggedIn:
                                    if(self.areUsersLoggedIn[user]):
                                        badge = user.split(".")
                                        sending = sending+":"+badge[0]
                                s.send(self.convertToBytes(sending))

                            print("   %s: %s" % (self.clientText[s], message))
                            if s not in self.outputs:
                                self.outputs.append(s)
                        else:
                            try:
                                if self.areUsersLoggedIn[self.clients[s] + ".txt"] is True:
                                    print("Client already logged in else where")
                                    self.closingClient(s, "logged in else where", s)
                            except:
                                continue
                            else:
                                print("Cannot allow client")
                                self.closingClient(s,"Client not allowed",s)
                    else:
                        self.closingClient(s,"Disconnect",s)

            for s in writable:
                try:
                    nextMsg = self.dataQueue[s].get_nowait()
                except queue.Empty:
                    #print("   Output queue Is empty for: ",s.getpeername())
                    self.outputs.remove(s)
                else:
                    print("   Sending: >%s< to %s" % (self.convertToString(nextMsg),self.clients[s]))
                    s.send(nextMsg)

            for s in e:
                print("   Handling exception for: ",s.getpeername())
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
                del self.dataQueue[s]

    def clearCustomDicts(self,con):
        print("Deleting user")
        #print(con)
        #print(self.clients)
        #not working correct
        self.areUsersLoggedIn[self.clients[con] + ".txt"] = False
        print(self.areUsersLoggedIn)
        del self.clientsIP[self.clients[con]]
        del self.clients[con]
    def closingClient(self,s,message,con=None):
        print(con)
        if con != None and con in self.clients:
            try:
                print("Closing "+self.clients[con]+" for: "+message)
                self.clearCustomDicts(con)
            except Exception:
                print("Closing Client for: " + message)
        else:
            print("Closing Client for: "+message)
            #self.clearCustomDicts(peer)
        if s in self.outputs:
            self.outputs.remove(s)
        self.inputs.remove(s)
        s.close()
        del self.dataQueue[s]
    def convertToString(self,bite):
        str = bite.decode("utf-8")
        return str
    def convertToBytes(self,str):
        byteStr = bytes(str,'utf-8')
        return byteStr
    def checkIfLoggedIn(self, data, client):
        b = False
        #Badge:000000
        try:
            s = self.convertToString(data).split(":")
            print(s)
            #is this a login attempt
            if(s[0].lower() == "badge"):
                for user in self.validUsers:
                    #is it a valid user
                    if s[1]+".txt" == user and self.areUsersLoggedIn[user] == False:
                        #if valid user set as logged in
                        self.areUsersLoggedIn[user] = True
                        b = True
                        break
                    else:
                        b = False
            else:
                return False, "invalid"
            return b, s[1]
        except:
            return False, "invalid"