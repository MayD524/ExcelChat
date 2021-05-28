
from _thread import *
from tkinter import constants
import prof_check
import userLogin
import socket
import time
import UPL
import os


class ServerCode:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
        self.ThreadCount = 0
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.profCheck = prof_check.profCheck({})        
        
        self.serverConfig = UPL.Core.file_manager.getData_json('config/config.json')
        self.LOGFILE = "log.log"
        self.DATAFILE = "main_data.txt"
        
        self.logQueue = []
        self.clients = []
        self.names = {}
        
        try:
            self.ServerSocket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))  

    ## used for logging
    def LoggingThread(self):
        while True:
            tmp = UPL.Core.file_manager.read_file(self.LOGFILE)
            data = '\n'.join(self.logQueue)
            data = tmp + data
            print(data)
            UPL.Core.file_manager.write_file(self.DATAFILE, data)
            self.logQueue = []
            time.sleep(self.serverConfig["LogTimer"])

    ## log all connections
    def logConnection(self, address):
        newConnection = f"[LOG] <{time.time()}> User : {address[0]}:{address[1]} has logged on"
        self.logQueue.append(newConnection)
    
    ## send a message to every user in the room
    def broadcastMessage(self, message):
        for client in self.clients:
            client.send(message)
    
    def ThreadedClient(self, connection, address):
        
        ## some house keeping stuff
        self.logConnection(address)
        
        ## generic stuff for login handleing
        ## get users name
        connection.send("NAME".encode('utf-8'))
        name = connection.recv(2048).decode('utf-8')
        
        ## get the password
        connection.send("PWORD".encode('utf-8'))
        pword = connection.recv(10240).decode('utf-8')
        
        ## append stuff 
        self.names[name] = f"{address[0]}:{address[1]}"
        self.clients.append(connection)
        
        ## user failed creds
        if userLogin.userLogin(name, pword) == False:
            connection.send("DECLINED".encode('utf-8'))
            self.clients.remove(connection)
            connection.close()
            return False
        
        ## user has correct creds
        else:
            connection.send("ACCEPTED".encode('utf-8'))
        
        ## The user has successfully logged in!
        self.broadcastMessage(f"{name} has joined the room".encode('utf-8'))
        
        try:
            while True:
                data = connection.recv(2048)
                ## just pass it back if nothing is wrong
                data = self.profCheck.check_prof(data.decode('utf-8'), name).encode('utf-8')
                self.broadcastMessage(data)
                
        except Exception:
            self.client.remove(connection)
            self.name.remove(name)
            connection.close()

    def ServerMain(self):
        print('Waiting for connections...')
        self.ServerSocket.listen(5)
        start_new_thread(self.LoggingThread, ())
        while True:
            Client, address = self.ServerSocket.accept()
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(self.ThreadedClient, (Client, address))
            self.ThreadCount += 1
            print('Thread number: ' + str(self.ThreadCount))
            
        self.ServerSocket.close()

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 1233
    server = ServerCode(HOST, PORT)
    server.ServerMain()