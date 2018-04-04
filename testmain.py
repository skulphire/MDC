from scripts import serverSelect
if __name__ == '__main__':
    server = serverSelect.serverHandle()
    try:
        server.start()
    except KeyboardInterrupt:
        exit(0)