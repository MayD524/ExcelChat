from datetime import datetime
import time
import UPL
import os


class ChatLogger:
    def __init__(self, LogFile, ChatName, settings, term):
        self.LogFile     = LogFile
        self.ChatName    = ChatName
        self.settings    = settings
        self.term        = term
        self.logBuffer   = []
        self.lastMessage = ''
    
    def newConnection(self, uName, IP, port):
        newLog = f"[{datetime.now()}] [NEW_USER] {uName} - {IP}:{port} has connected to the server"
        self.logBuffer.append(newLog)
        self.term.queue_append(newLog)
        print(newLog)
    
    def userDisconnect(self, uName,data):
        newLog = f"[{datetime.now()}] [DISCONNECT] {uName} - {data}"
        self.logBuffer.append(newLog)
        self.term.queue_append(newLog)
        print(newLog)
    
    def packet_log(self, packet):
        newLog = f'[{datetime.now()}] [PACKET_RECV] {packet}'
        self.logBuffer.append(newLog)
        self.term.queue_append(newLog)
        print(newLog)
    
    def newChat(self, uName, msg, flagged):
        if msg == '':
            return
        newLog = f"[{datetime.now()}] [NEW_CHAT] {uName} - \"{msg}\" Flag:{flagged}"
        self.logBuffer.append(newLog)
        self.term.queue_append(newLog)
        print(newLog)
    
    def error(self, error):
        newlog = f"[{datetime.now()}] [ERROR] There was an error with connection : {error}"
        self.logBuffer.append(newlog)
        self.term.queue_append(newlog)
        print(newlog)
    
    def autoLog(self, timer):
        self.logBuffer.append(f"[{datetime.now()}] [LOGGER_START] Chat Logger has started")
        self.term.queue_append(f"[{datetime.now()}] [LOGGER_START] Chat Logger has started")
        while True:
            if len(self.logBuffer) >= 1:
                
                print(f"[{datetime.now()}] [LOGGER_OUTPUT] outputing to {self.LogFile}")
                self.term.queue_append(f"[{datetime.now()}] [LOGGER_OUTPUT] outputing to {self.LogFile}")
                tmp = '\n'.join(self.logBuffer)
                ## reset logBuffer
                self.logBuffer = []
                
                with open(self.LogFile, "a") as writer:
                    tmp = "\n" + tmp
                    writer.write(tmp)
            
            ## Time duration
            time.sleep(timer)