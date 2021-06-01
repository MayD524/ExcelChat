from _thread import *
from tkinter import *
import UPL

class terminalControler:
    def __init__(self):
        self.text_queue = []
        self.test_msg = ''
    
    def get_queue(self):
        tmp = self.text_queue
        self.text_queue = []
        return tmp
    
    def queue_append(self, data):
        self.text_queue.append(data)

class Terminal:
    def __init__(self, controller):
        self.controller   = controller
        self.running      = True
        self.config       = UPL.Core.file_manager.getData_json("config/config.json")
        self.GUI_settings = {
            "icon_image" : "C:\\Users\\Cross\\Pictures\\Downloads\\0.png",
            "background" : "#17202A",
            "forground" : "#EAECEE",
            "font" : "Helvetica",
            "height": 500,
            "width": 700
        }
        self.Window = Tk()
        self.Window.withdraw()
        ## draw the elements of the window
        self.layout()
        start_new_thread(self.recv, ())
        
        self.Window.mainloop()
    
    def layout(self): 
        # to show chat window 
        self.Window.deiconify() 
        self.Window.title(f"Excel Chat Admin Terminal")
        self.Window.resizable(width = True, 
                            height  = True) 
        self.Window.configure(width = self.GUI_settings['width'], 
                            height  = self.GUI_settings['height'], 
                            bg         = self.GUI_settings["background"]) 
  
        ## change self.name to room name
        self.labelHead = Label(self.Window, 
                            bg              = self.GUI_settings["background"], 
                            fg              = self.GUI_settings["forground"], 
                            textvariable = "test", 
                            font          = "Helvetica 13 bold", 
                            pady         = 5) 
        
        self.labelHead.place(relwidth = 1) 
        self.line = Label(self.Window, 
                        width = 450, 
                        bg       = "#ABB2B9") 
        
        self.line.place(relwidth  = 1, 
                        rely       = 0.07, 
                        relheight = 0.012) 
        
        self.textCons = Text(self.Window, 
                            width  = 20, 
                            height = 2, 
                            bg     = self.GUI_settings["background"], 
                            fg     = self.GUI_settings["forground"], 
                            font   = f"{self.GUI_settings['font']} 14", 
                            padx   = 5, 
                            pady   = 5) 
        
        self.textCons.place(relheight = 0.745, 
                            relwidth  = 1, 
                            rely      = 0.08) 
        
        self.labelBottom = Label(self.Window, 
                                bg     = "#ABB2B9", 
                                height = 80) 
        
        self.labelBottom.place(relwidth = 1, 
                               rely     = 0.825) 
        
        self.entryMsg = Entry(self.labelBottom, 
                              bg   = "#2C3E50", 
                              fg   = self.GUI_settings["forground"], 
                              font = f"{self.GUI_settings['font']} 13") 
        
        # place the given widget 
        # into the gui window 
        self.entryMsg.place(relwidth  = 0.74, 
                            relheight = 0.06, 
                            rely      = 0.008, 
                            relx      = 0.011) 
        
        self.entryMsg.focus() 
        
        # create a Send Button 
        self.buttonMsg = Button(self.labelBottom, 
                                text    = "Send", 
                                font    = f"{self.GUI_settings['font']} 10 bold", 
                                width   = 20, 
                                bg      = "#ABB2B9", 
                                command = lambda : self.getInput(self.entryMsg.get())) 
        
        self.buttonMsg.place(relx      = 0.77, 
                             rely      = 0.008, 
                             relheight = 0.06, 
                             relwidth  = 0.22) 
        
        self.textCons.config(cursor = "arrow") 


        # create a scroll bar 
        scrollbar = Scrollbar(self.textCons) 
        
        # place the scroll bar 
        # into the gui window 
        scrollbar.place(relheight = 1, 
                        relx      = 0.974) 
        
        scrollbar.config(command = self.textCons.yview) 
        self.textCons.tag_config("highlight", background="gold", foreground="black")
        self.textCons.config(state = DISABLED) 
        
    def getInput(self, text):
        self.controller.test_msg = text
        self.controller.queue_append(text)
        self.entryMsg.delete(0, END)
    
    def recv(self):
        while True:
            queue = self.controller.get_queue()
            if len(queue) > 0:
                for i in queue:
                    self.display_text(i)
                
    def display_text(self, text):
        if text == '':
            return
        
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, text+'\n')
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
        self.entryMsg.delete(0, END)