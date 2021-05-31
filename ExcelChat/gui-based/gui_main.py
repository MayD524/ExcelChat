# import all the required modules 
from tkinter import *
from tkinter import font 
from tkinter import ttk
import playsound
import threading
import socket
import psutil 
import UPL
import os

from pyautogui import printInfo

class Login:
	def __init__(self):
		self.login = Tk()

		# set the title
		self.login.title("Login")
		self.login.resizable(width=False, height=False)
		self.login.configure(width=400, height=300)
		# create a Label
		self.pls = Label(self.login, text="Please login to continue", justify=CENTER, font="Helvetica 14 bold")

		self.pls.place(relheight=0.15, relx=0.2, rely=0.07)
		# create a Label
		self.labelName = Label(self.login, text="Name: ", font="Helvetica 12")

		self.labelName.place(relheight=0.2, relx=0.1, rely=0.2)

		# create a entry box for
		# typing the message
		self.entry2 = Entry(self.login, font="Helvetica 14", show="*")

		self.entry2.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.4)

		self.label2 = Label(self.login, text="Password: ", font="Helvetica 12")

		self.label2.place(relheight=0.2, relx=0.1, rely=0.4)

		# create a entry box for
		# typing the message
		self.entryName = Entry(self.login, font="Helvetica 14")

		self.entryName.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.2)

		# set the focus of the cursor
		self.entryName.focus()

		# create a Continue Button
		# along with action
		self.go = Button(self.login, text="Login", font="Helvetica 14 bold",
						 command=lambda: self.loginFunc(self.entryName.get(), self.entry2.get()))

		self.go.place(relx=0.4, rely=0.55)

		self.login.bind("<Return>", self.clickLogin)

		self.login.mainloop()
	
	def loginFunc(self, uName, pWord):
		if uName == '':
			UPL.gui.popup("You cannot have a null name")
			return

		if pWord == '':
			UPL.gui.popup('You cannot have a null password')
			return
		
		self.goAhead(uName, pWord)
	
	def clickLogin(self, event):
		self.go.invoke()
		
	def goAhead(self, name, pword):
		self.login.destroy()
		ChatGUI(name, pword)

# CHATGUI class for the chat 
class ChatGUI: 
	# constructor method 
	def __init__(self, name, password): 
		self.name = name
		self.pwd = password
		self.currentRoom = "MAIN"
		self.running = True
		self.msg = None
  
		self.config = UPL.Core.file_manager.getData_json("config/config.json")
		self.GUI_settings = self.config['GUI']
		self.note_settings = self.config['notifications']
		# chat window which is currently hidden 
		self.Window = Tk() 
		self.Window.withdraw() 
		self.HeaderText = StringVar()
		self.HeaderText.set(self.name)
		self.layout()

		## Start thread for receiving messages
		rcv = threading.Thread(target=self.receive)
		rcv.start()

		## mainloop
		self.Window.mainloop()
		self.ChatExit()
  
	# The main layout of the chat 
	def layout(self): 
		# to show chat window 
		self.Window.deiconify() 
		self.Window.title("Excel Chat")
  
		if self.GUI_settings["icon_image"] != "default":
			windowIcon = PhotoImage(file=self.GUI_settings["icon_image"])
			self.Window.iconphoto(False, windowIcon)
		self.Window.resizable(width = False, 
							height = False) 
		self.Window.configure(width = self.GUI_settings['width'], 
							height = self.GUI_settings['height'], 
							bg = self.GUI_settings["background"]) 
  
		## change self.name to room name
		self.labelHead = Label(self.Window, 
							bg = self.GUI_settings["background"], 
							fg = self.GUI_settings["forground"], 
							textvariable = self.HeaderText, 
							font = "Helvetica 13 bold", 
							pady = 5) 
		
		self.labelHead.place(relwidth = 1) 
		self.line = Label(self.Window, 
						width = 450, 
						bg = "#ABB2B9") 
		
		self.line.place(relwidth = 1, 
						rely = 0.07, 
						relheight = 0.012) 
		
		self.textCons = Text(self.Window, 
							width = 20, 
							height = 2, 
							bg = self.GUI_settings["background"], 
							fg = self.GUI_settings["forground"], 
							font = f"{self.GUI_settings['font']} 14", 
							padx = 5, 
							pady = 5) 
		
		self.textCons.place(relheight = 0.745, 
							relwidth = 1, 
							rely = 0.08) 
		
		self.labelBottom = Label(self.Window, 
								bg = "#ABB2B9", 
								height = 80) 
		
		self.labelBottom.place(relwidth = 1, 
							rely = 0.825) 
		
		self.entryMsg = Entry(self.labelBottom, 
							bg = "#2C3E50", 
							fg = self.GUI_settings["forground"], 
							font = f"{self.GUI_settings['font']} 13") 
		
		# place the given widget 
		# into the gui window 
		self.entryMsg.place(relwidth = 0.74, 
							relheight = 0.06, 
							rely = 0.008, 
							relx = 0.011) 
		
		self.entryMsg.focus() 
		
		# create a Send Button 
		self.buttonMsg = Button(self.labelBottom, 
								text = "Send", 
								font = f"{self.GUI_settings['font']} 10 bold", 
								width = 20, 
								bg = "#ABB2B9", 
								command = lambda : self.sendButton(self.entryMsg.get())) 
		
		self.buttonMsg.place(relx = 0.77, 
							rely = 0.008, 
							relheight = 0.06, 
							relwidth = 0.22) 
		
		self.textCons.config(cursor = "arrow") 

		self.menu = Menu(self.Window)
		self.Window.config(menu=self.menu)

		chat_menu = Menu(self.menu)
		self.menu.add_cascade(label="Chats", menu=chat_menu)

		chat_menu.add_command(label='Change Chat', command=self.SelectRoom)
		chat_menu.add_command(label='Join Room', command=self.JoinRoom)
  

		# create a scroll bar 
		scrollbar = Scrollbar(self.textCons) 
		
		# place the scroll bar 
		# into the gui window 
		scrollbar.place(relheight = 1, 
						relx = 0.974) 
		
		scrollbar.config(command = self.textCons.yview) 
		self.textCons.tag_config("highlight", background="gold", foreground="black")
		self.textCons.config(state = DISABLED) 
		self.Window.bind('<Return>', self.sendMessage)

	def SelectRoom(self):
		print(self.userData["rooms"])

	def JoinRoom(self):
		roomCode = UPL.gui.prompt("Join room", "Enter the room code!")

		if roomCode == "":
			UPL.gui.popup("That is an invalid room code!")
			return

		self.sendPacket(f"ROOMCODE:{roomCode}", 'SERVER', "SERVER")

	## here is where any last minute logs should happen
	def ChatExit(self):
		client.close()
		cpid = os.getpid()
		TSys = psutil.Process(cpid)
		TSys.terminate()

	# function to basically start the thread for sending messages 
	def sendButton(self, msg): 
		self.textCons.config(state = DISABLED) 
		self.msg = msg 

		snd = threading.Thread(target = self.sendMessage) 
		snd.start() 

	def notifications(self,message:str, pinged:bool):
		if self.note_settings["soundNotification"] == True:
			if self.note_settings["allowed_notifications"] == "all":
				playsound.playsound(self.note_settings['soundNotification_location'])
			elif self.note_settings['allowed_notifications'] == "ping_only" and pinged == True:
				playsound.playsound(self.note_settings['soundNotification_location'])
	# function to receive messages 
	def receive(self): 
		while self.running: 
			try: 
				message = client.recv(2048).decode(FORMAT) 

				## fix me (users can send this and will cause issues)
				if message.startswith("SERVERNAME:"):
					message = message.split(":")[1]
					continue
 
				elif message.startswith('USERDATA:'):
					message = message.split(':',1)[1]
					self.userData = eval(message)
					del self.userData['pwd']
					continue
				
				if "SERVER_ACCEPTED" in message:
					message = message.replace('SERVER_ACCEPTED', '')

				match message:
					## send the username to the server
					case 'NAME':
						self.sendPacket(self.name, "SERVER", "ServerInfo")
						continue
					
					## send the password to the server
					case 'PWORD':
						self.sendPacket(self.pwd, "SERVER", "ServerInfo")
						del self.pwd
						continue
					
					## User was declined access to to bad creds
					case "DECLINED":
						UPL.gui.popup("Your access was declined (incorrect user or password)", "Something went wrong!")
						self.ChatExit()
      
					## Every other message. Display text in main chat area
					case _:
						pinged = True if f"@{self.name}" in message else False
   
						# insert messages to text box 
						self.textCons.config(state = NORMAL) 

						if pinged == False:
							self.textCons.insert(END, message+"\n\n") 
       
						else:
							self.textCons.insert(END, message+'\n\n', ('highlight',))
						self.textCons.config(state = DISABLED) 
						self.textCons.see(END) 
  
			except Exception as e:
				print(e)
				# an error will be printed on the command line or console if there's an error 
				print("An error occured!") 
				client.close() 
				break

	def sendPacket(self, data, sendType, sendTo):
		if data == '':
			UPL.gui.popup("You cannot send null data", "Something Went Wrong")

		packet = {
			"data" : data,
			"type" : sendType,
			"to"   : sendTo,
			"from" : self.name
		}
	
		message = str(packet).encode(FORMAT)
		while True:
			client.send(message)
			break
  
	# function to send messages 
	def sendMessage(self, *args): 
		if not self.msg:
			self.msg = self.entryMsg.get()

		if self.msg == '':
			return
   
		## this will run as a command
		if self.msg.startswith('/'):
			self.msg = self.msg.replace('/','',1)
			
			if self.msg == "exit":
				client.send(f"DISCONNECT:{self.name}".encode('utf-8'))
				self.Window.destroy()
				self.running = False
				self.ChatExit()
   
			self.entryMsg.delete(0, END)
			return
   
		## send chats
		self.textCons.config(state=DISABLED) 
		self.sendPacket(self.msg, "CHAT", self.currentRoom)
		self.entryMsg.delete(0, END)
		self.msg = None

if __name__ == "__main__":
	PORT = 1233
	SERVER = "127.0.0.1"
	print(f"Connecting to: {SERVER}:{PORT}")
	ADDRESS = (SERVER, PORT) 
	FORMAT = "utf-8"

	# Create a new client socket 
	# and connect to the server 
	client = socket.socket(socket.AF_INET, 
						socket.SOCK_STREAM) 
	client.connect(ADDRESS) 

	l = Login()
 
else:
	raise ImportError("This is the main file you cannot import this file.")