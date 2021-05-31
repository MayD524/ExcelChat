import UPL


def userLogin(name, pword):
    users = UPL.Core.file_manager.getData_json("config/users.json")
    
    if name in users.keys():
        if pword in users[name]["pwd"]:
            return True
        
    return False