import time
import json
import os


class file_updater:
    def __init__(self, timer):
        self.timer = timer
        ## file : data
        self.queue = {}
        
    def add_queue(self, filename, data):
        if not filename.endswith('.json'):
            if type(data) != str:
                data = str(data)        
        
        self.queue[filename] = data
    
    def run_updater(self):
        while True:
            if len(self.queue.keys()) > 0:
                for key in self.queue.keys():
                    try:
                        if key.endswith('.json'):
                            with open(key, "w") as jsonwriter:
                                json.dump(self.queue[key], jsonwriter, indent=4)
                                
                        else:
                            with open(key, "a") as writer:
                                writer.write(self.queue[key])
                    except Exception:
                        pass
                                    
                self.queue.clear()
            
            time.sleep(self.timer)