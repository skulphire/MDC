from scripts import SocketHandler

if __name__ == '__main__':
    socket = SocketHandler.SocketHandle()
    socket.clientConnect()
    socket.clientSendRecv("Messsage 1")
    socket.clientSendRecv("Messsage 0")
    socket.clientSendRecv("Messsage 2")
    socket.clientSendRecv("Messsage 3")
    socket.clientClose()