from scripts import SocketHandler

if __name__ == '__main__':
    socket = SocketHandler.SocketHandle()
    try:
        socket.createServer()
    except KeyboardInterrupt:
        socket.closeServer()