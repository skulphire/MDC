from socket import *

class SocketHandle(object):
    def __init__(self):
        # server: "35.172.19.17"
        # 184 is desktop
        # 69 is laptop
        self.s = socket(AF_INET,  SOCK_STREAM)
        self.server = socket(AF_INET, SOCK_STREAM)
        #to reuse socket fast
        #self.server.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)

    def clientConnect(self):
        try:
            self.s.connect(("35.172.19.17", 9130))
            print("connected")
            return True
        except Exception:
            print("Could not connect")
            return False

    def clientSendRecv(self, message):
        self.s.send(self.convertToBytes(message))
        data = self.convertToString(self.s.recv(1024))
        print("server: " + data)

    def clientClose(self):
        self.s.send(self.convertToBytes("done"))
        data = self.convertToString(self.s.recv(1024))
        print("server: " + data)
        if data == "Recieved":
            print("Done")
            self.s.close()
        else:
            print("##############")
            #self.s.close()

    def createServer(self):
        test = True
        while test:
            try:
                self.server.bind(("172.31.82.100",9130))
                test = False
            except:
                self.server.bind(("172.31.82.100",8888))

        print("port:", self.server.getsockname())

        while True:
            self.server.listen(1)
            print("Listening")
            try:
                connection, addr = self.server.accept()
                print("Connected by: ", addr)
            except:
                continue
            while connection:
                try:
                    data = connection.recv(1024)
                    if data:
                        print("Client: "+self.convertToString(data))
                    if data == "done":
                        connection.sendall(self.convertToBytes("Recieved"))
                    else:
                        connection.sendall(self.convertToBytes(">"))
                except Exception:
                    #print("Finished")
                    connection.close()
                    break

    def closeServer(self):
        self.server.close()
    def convertToBytes(self,str):
        byteStr = bytes(str,'utf-8')
        return byteStr
    def convertToString(self,bite):
        str = bite.decode("utf-8")
        return str