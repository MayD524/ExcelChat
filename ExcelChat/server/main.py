from _thread import *
from tkinter import constants
import file_update
import ChatLogger
import prof_check
import userLogin
import terminal
import socket
import psutil 
import UPL
import os

## change top name to host name

class ServerCode:
    def __init__(self, host, port, config):
        self.host       = host
        self.port       = port
        self.config     = config
        self.termCont   = terminal.terminalControler()
        self.logger     = ChatLogger.ChatLogger("log.log", self.config["Name"], self.config, self.termCont)
        self.file_upate = file_update.file_updater(self.config["Update_Timer"])
        
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.profCheck    = prof_check.profCheck({})        
        
        self.serverConfig = UPL.Core.file_manager.getData_json('config/config.json')
        
        start_new_thread(self.logger.autoLog, (self.config["LogTimer"],))
        start_new_thread(self.file_upate.run_updater, ())
        start_new_thread(terminal.Terminal, (self.termCont, ))
        start_new_thread(self.terminal_input_thread, ())
        
        self.user_data = UPL.Core.file_manager.getData_json('config/users.json')
        self.clients   = {
            ## "name" : connection
        }
        self.names     = {}
        self.chats     = UPL.Core.file_manager.getData_json('config/rooms.json')
        
        self.userfile  = 'config/users.json'
        self.userData  = UPL.Core.file_manager.getData_json(self.userfile)
        
        try:
            self.ServerSocket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))  
    
    def terminal_input_thread(self):
        lst = ''
        while True:

            if lst != self.termCont.test_msg:
                tmp = self.termCont.test_msg
                
                if tmp.startswith('msg:'):
                    tmp = tmp.split(':',1)[1]
                    self.broadcastMessage(f"SERVER: {tmp}", 'all')
                    
                elif tmp == 'exit':
                    self.broadcastMessage(f"SERVER: server shutting down!", 'all')
                    self.ServerSocket.close()
                    psutil.Process(os.getpid()).terminate()   
                
                elif tmp.startswith("new_room:"):
                    tmp = tmp.split(':',1)[1].strip()
                    if tmp == 'all':
                        self.termCont.queue_append('You cannot add the room "all"')
                        return
                    code = UPL.Core.generate_code(10)
                    self.termCont.queue_append(f"Code for {tmp} is {code}")
                    roomsC = UPL.Core.file_manager.getData_json('config/room_codes.json')
                    rooms = UPL.Core.file_manager.getData_json('config/rooms.json')
                    roomsC[code] = tmp 
                    rooms[tmp] = []
                    self.chats[tmp] = []
                    
                    self.file_upate.add_queue("config/rooms.json", rooms)
                    self.file_upate.add_queue("config/room_codes.json", roomsC)
                lst = self.termCont.test_msg
    
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
    def broadcastMessage(self, message, room):
        if room not in self.chats.keys():
            self.logger.error(f'There was an issue with rooms, {room} does not exist')
            return

        room = self.chats[room]
        for client in self.clients.keys():

            if client in room:
                if type(message) == str:
                    message = message.encode('utf-8')
                self.clients[client].send(message)
                
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
        self.names[name] = self.userData[name]['current_room']
        self.clients[name] = connection
        
        ## the chats the user is in
        self.chats[self.names[name]].append(name)
        self.chats['all'].append(name)
        ## user failed creds
        if userLogin.userLogin(name, pword) == False or pword == '':
            connection.send("DECLINED".encode('utf-8'))
            del self.clients[name]
            connection.close()
            return False
        
        ## user has correct creds
        else:
            self.userData[name]['online'] = True
            self.file_upate.add_queue(self.userfile, self.userData)
            connection.send("SERVER_ACCEPTED".encode('utf-8'))
        
        ## The user has successfully logged in!
        self.broadcastMessage(f"{name} has joined the room".encode('utf-8'), self.userData[name]['current_room'])
        
        try:
            while True:
                pack_data = self.process_packet(connection, "any", 2048)
                
                data = pack_data["data"]
                
                if pack_data['type'] == "CHAT":
                    if len(data) > 2048:
                        data = data[:2048]

                    if data.startswith("DISCONNECT:"):
                        self.broadcastMessage(f"{name} has disconnected", pack_data['to'])
                        self.logger.userDisconnect(name, data)
                        connection.close() 
                    
                    org_msg = data
                    data = self.profCheck.check_prof(data, name)
                    
                    self.logger.newChat(name, org_msg, data[0])
                    message = f"{pack_data['from']} : {data[1]}".encode('utf-8')
                    self.broadcastMessage(message, pack_data['to'])
                
                elif pack_data['type'] == "SERVER":
                    if data.startswith("ROOMCODE:"):
                        code = data.split(':')[1]
                        rooms = UPL.Core.file_manager.getData_json("config/room_codes.json")
                        
                        if code in rooms.keys():
                            self.userData[name]['rooms'].append(rooms[code])
                            self.file_upate.add_queue(self.userfile, self.userData)
                            connection.send(f"USERDATA:{self.userData[name]}".encode('utf-8')) 
        
                    elif data.startswith("SWITCHROOM:") or data.startswith("SETROOM:"):
                        room = data.split(':')[1]
                        if room in self.chats.keys():
                            self.chats[room].append(name)
                            self.chats[self.names[name]].remove(name)
                            self.broadcastMessage(f"{name} has left the chat", self.names[name])
                            self.names[name] = room 
                            self.userData[name]['current_room'] = room
                            self.file_upate.add_queue(self.userfile, self.userData)
                            self.broadcastMessage(f"{name} has joined the chat", room)
                            connection.send(f"USERDATA:{self.userData[name]}".encode('utf-8'))
                            
        except Exception:
            ## this will run any time the user has disconnected
            self.logger.userDisconnect(name, f"{name} has disconnected")
            self.userData[name]['online'] = False
            self.file_upate.add_queue(self.userfile, self.userData)
            self.chats[self.names[name]].remove(name)
            self.chats['all'].remove(name)
            connection.close()
            self.broadcastMessage(f"{name} has disconnected from chat".encode('utf-8'), self.userData[name]['current_room'])
            del self.clients[name]
            del self.names[name]

    def ServerMain(self):
        print('Waiting for connections...')
        self.ServerSocket.listen(5)
        
        ## this loop pauses while waiting for new connection
        while True:
            tmp = UPL.Core.file_manager.getData_json(self.userfile)
            if self.userData != tmp:
                self.userData = tmp
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
    