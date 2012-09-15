from module import Module
import redis

class Ignore(Module):
    def __init__(self):
        self.modname = "Ignore"
        self.priority = 0       
        self.r = redis.Redis()
        self.commands = dict()
    
        self.add_command(".ignore", self.add_ignore)
        self.add_command(".unignore", self.unignore)
        self.add_command(".list_ignored", self.list_ignored)
    
    def add_ignore(self, cmd, msg, user, arg):
        if not self.is_admin(self.get_username(user)):
            return self.ignore()
        
        self.r.sadd("ircbot_ignored", arg[0])
        return self.send_message(arg[0] + " ignored")
            
    def unignore(self, cmd, msg, user, arg):
        if not self.is_admin(self.get_username(user)):
            return self.ignore()
            
#       self.r.srem("ircbot_ignored", arg[0])
#       return self.send_message(arg[0] + " unignored")
    
    def list_ignored(self, cmd, msg, user, arg):
        return self.send_message(", ".join(self.r.smembers("ircbot_ignored")))
        
    def parse_custom(self, msg, cmd, user, arg):
        ignored = self.r.smembers("ircbot_ignored")
            
        for ignoree in ignored:
            if ignoree in user:
                return self.generate_response() # discard message               

        
