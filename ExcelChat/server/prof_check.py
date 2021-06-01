import UPL
## for profanity filtering and other stuff like that
class profCheck:
    def __init__(self, policy):
        self.policy     = policy
        self.prof_words = UPL.Core.file_manager.clean_read('prof_words.txt')
        
        
    def check_prof(self, message, user):
        hasCursed = False
        for word in self.prof_words:
            if word in message:
                message = message.replace(word, ''.join('*' for x in word))
                hasCursed = True
        return (hasCursed, message)