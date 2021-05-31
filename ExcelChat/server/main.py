
from _thread import *
from tkinter import constants 
import file_update
import ChatLogger
import prof_check
import userLogin
import socket
import UPL
import os

## change top name to host name

class ServerCode:
    def __init__(self, host, port, config):
        self.host = host
        self.port = port
        self.config = config
        self.logger = ChatLogger.ChatLogger("log.log", self.config["Name"], self.config)
        self.file_upate = file_update.file_updater(self.config["Update_Timer"])
        
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.profCheck = prof_check.profCheck({})        
        
        self.serverConfig = UPL.Core.file_manager.getData_json('config/config.json')
        
        start_new_thread(self.logger.autoLog, (self.config["LogTimer"], ))
        start_new_thread(self.file_upate.run_updater, ())
        
        self.user_data = UPL.Core.file_manager.getData_json('config/users.json')
        self.clients = []
        self.names = {}
        self.chats = {
            ##"room" : ["users"]
        }
        
        self.userfile = 'config/users.json'
        self.userData = UPL.Core.file_manager.getData_json(self.userfile)
        
        try:
            self.ServerSocket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))  
    
    def process_packet(self, connection, typeExpected, bufSize):
        packet_data = connection.recv(bufSize).decode('utf-8')

        packet_data = eval(packet_data)
        self.logger.packet_log(packet_data)
            
        if packet_data["type"] == typeExpected:
           return packet_data['data']
            
        elif typeExpected == "any":
            return packet_data
            
        else:
            self.logger.error(f"Incorrect type, expected {typeExpected} got {packet_data['type']} from {packet_data['from']}")
            
    ## send a message to every user in the room
    def broadcastMessage(self, message):
        for client in self.clients:
            client.send(message)
    
    def ThreadedClient(self, connection, address):
        ## generic stuff for login handleing
        ## get users name
        connection.send("NAME".encode('utf-8'))
        name = self.process_packet(connection, "SERVER", 2048)
        
        ## get the password
        connection.send("PWORD".encode('utf-8'))
        pword = self.process_packet(connection, "SERVER", 10240)
        connection.send(f"SERVERNAME:{self.config['Name']}".encode('utf-8'))
        connection.send(f"USERDATA:{self.userData[name]}".encode('utf-8'))
        
        self.logger.newConnection(name, address[0], address[1])
        ## append stuff 
        self.names[name] = f"{address[0]}:{address[1]}"
        self.clients.append(connection)
        
        ## user failed creds
        if userLogin.userLogin(name, pword) == False or pword == '':
            connection.send("DECLINED".encode('utf-8'))
            self.clients.remove(connection)
            connection.close()
            return False
        
        ## user has correct creds
        else:
            self.userData[name]['online'] = True
            self.file_upate.add_queue(self.userfile, self.userData)
            connection.send("SERVER_ACCEPTED".encode('utf-8'))
        
        ## The user has successfully logged in!
        self.broadcastMessage(f"{name} has joined the room".encode('utf-8'))
        
        try:
            while True:
                pack_data = self.process_packet(connection, "any", 2048)
                
                data = pack_data["data"]
                
                if pack_data['type'] == "CHAT":
                    if len(data) > 2048:
                        data = data[:2048]

                    if data.startswith("DISCONNECT:"):
                        self.broadcastMessage(f"{name} has disconnected")
                        self.logger.userDisconnect(name, data)
                        connection.close() 
                        
                    org_msg = data
                    data = self.profCheck.check_prof(data, name)
                    
                    self.logger.newChat(name, org_msg, data[0])
                    message = f"{pack_data['from']} : {data[1]}".encode('utf-8')
                    self.broadcastMessage(message)
                
                elif pack_data['type'] == "SERVER":
                    if data.startswith("ROOMCODE:"):
                        code = data.split(':')[1]
                        rooms = UPL.Core.file_manager.getData_json("config/room_codes.json")
                        
                        if code in rooms.keys():
                            self.userData[name]['rooms'].append(rooms[code]['name'])
                            self.file_upate.add_queue(self.userfile, self.userData)
                            connection.send(f"USERDATA:{self.userData[name]}".encode('utf-8')) 
        except Exception:
            ## this will run any time the user has disconnected
            self.logger.userDisconnect(name, f"{name} has disconnected")
            self.userData[name]['online'] = False
            self.file_upate.add_queue(self.userfile, self.userData)
            self.clients.remove(connection)
            connection.close()
            self.broadcastMessage(f"{name} has disconnected from chat".encode('utf-8'))
            del self.names[name]

    def ServerMain(self):
        print('Waiting for connections...')
        self.ServerSocket.listen(5)
        while True:
            Client, address = self.ServerSocket.accept()
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(self.ThreadedClient, (Client, address))

        self.ServerSocket.close()
    
def socket_server(config):
    HOST = config["Host"]
    PORT = config["Port"]
    server = ServerCode(HOST, PORT, CONFIG)
    server.ServerMain()

if __name__ == "__main__":
    CONFIG = UPL.Core.file_manager.getData_json("config/config.json")
    socket_server(CONFIG)
    