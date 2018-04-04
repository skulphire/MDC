from scripts import serverSelect
if __name__ == '__main__':
    server = serverSelect.serverHandle()
    server.start()