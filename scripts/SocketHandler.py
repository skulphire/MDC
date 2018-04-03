from socket import *

class SocketHandle(object):
    def __init__(self):
        # server: "107.180.44.223"
        # 184 is desktop
        self.s = socket(AF_INET,  SOCK_STREAM)

    def clientConnect(self):
        try:
            self.s.connect(("192.168.1.69", 8889))
            print("connected")
        except Exception:
            print("Could not connect")

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
            print("<")
            #self.s.close()

    def createServer(self):
        server = socket(AF_INET, SOCK_STREAM)
        server.bind(("192.168.1.69",8889))


        while True:
            server.listen(1)
            print("Listening")
            try:
                connection, addr = server.accept()
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


    def convertToBytes(self,str):
        byteStr = bytes(str,'utf-8')
        return byteStr
    def convertToString(self,bite):
        str = bite.decode("utf-8")
        return str