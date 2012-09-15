from module import Module

class Operator(Module):
    def __init__(self):
        self.modname = "Operator"
        self.commands = dict()
        self.priority = 3
        
        self.add_command(".op", self.op)
        self.add_command(".deop", self.deop)
        self.add_command(".kick", self.kick)
        self.add_command(".ban", self.ban)
        self.add_command(".kickban", self.kickban)
        self.add_command(".unban", self.unban)
        
    def who(self, user, arg):
        try:
            who = arg[0]
        except:
            who = self.get_username(user)
        
        return who
        
    def who_complete(self, user, arg): 
        try: 
            who = arg[0]
        except:
            who = user
            
        return who
        
    def comment(self, arg):
        try:
            comment = " ".join(arg[1:])
        except:
            comment = ""
            
        return comment
    
    def op(self, msg, cmd, user, arg):
        who = self.who(user, arg)
            
        return self.send_raw_message("MODE " + self.config.get('core', 'home_channel') + " +o " + who) 
    
    def deop(self, msg, cmd, user, arg):
        who = self.who(user, arg)
            
        return self.send_raw_message("MODE " + self.config.get('core', 'home_channel') + " -o " + who)
    
    def kick(self, msg, cmd, user, arg):
        who = self.who(user, arg)
        if self.is_admin(who): 
            return self.ignore()
            
        comment = self.comment(arg)
    
        return self.send_raw_message("KICK " + self.config.get('core', 'home_channel') + " " + who + " :" + comment)
    
    def ban(self, msg, cmd, user, arg):
        who = self.who_complete(user, arg)
        
        return self.send_raw_message("MODE " + self.config.get('core', 'home_channel') + " +b " + who)
    
    def kickban(self, msg, cmd, user, arg):
        who = self.who(user, arg)
        if self.is_admin(who): 
            return self.ignore()
            
        comment = self.comment(arg)
        
        return self.recursion_with_raw_message("MODE " + self.config.get('core', 'home_channel') + " +b " + who + " " + comment, ".kick", user, [self.get_username(who), comment])
    
    def unban(self, msg, cmd, user, arg):
        who = self.who(user, arg)
        
        return self.send_raw_message("MODE " + self.config.get('core', 'home_channel') + " -b " + who)