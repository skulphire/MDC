from scripts import SocketHandler

if __name__ == '__main__':
    socket = SocketHandler.SocketHandle()
    socket.clientConnect()