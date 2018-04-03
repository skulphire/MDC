from socket import *

class SocketHandle(object):
    def __init__(self):
        self.s = socket(AF_INET,  SOCK_STREAM)
    def clientConnect(self):
        try:
            #server: "107.180.44.223"
            self.s.connect(("192.168.1.184", 8889))
            print("connected")
            self.s.send(self.convertToBytes("testing"))
            data = self.convertToString(self.s.recv(1024))
            print("server: "+data)
            if data == "Recieved":
                self.s.send(self.convertToBytes("done"))
                print("Done")
                self.s.close()
            else:
                print("No good")
                self.s.close()
        except Exception:
            print("Could not connect")

    def createServer(self):
        server = socket(AF_INET, SOCK_STREAM)
        server.bind(("192.168.1.184",8889))


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
                    print("Client: "+self.convertToString(data))
                    connection.sendall(self.convertToBytes("Recieved"))
                except Exception:
                    print("Finished")
                    connection.close()
                    break


    def convertToBytes(self,str):
        byteStr = bytes(str,'utf-8')
        return byteStr
    def convertToString(self,bite):
        str = bite.decode("utf-8")
        return str