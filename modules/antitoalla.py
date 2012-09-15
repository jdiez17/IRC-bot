from module import Module

class AntiToalla(Module):
    def __init__(self):
        self.modname = "AntiToalla"
                
    def prepare_toallas(self):
        self.toallas = open('/usr/share/toalla.txt')
        user = self.admins[0]
        new_toallas = []
        
        for toalla in self.toallas:
            this_toalla = toalla.replace("\n", "")
            this_toalla = this_toalla.replace("$1-", user)
            this_toalla = this_toalla.replace("$me", self.nick)
            this_toalla = this_toalla.replace("$network", "#fearnode") # fix hardcode
        
            new_toallas.append(this_toalla)
            
        self.toallas = new_toallas
        
    def parse_custom(self, msg, cmd, user, arg):
        if self.admins[0] in cmd:
            self.prepare_toallas()
        
            if msg.strip().lower() in self.toallas:
                return self.recursion_no_message(".toalla", user, [self.get_username(user)])
            else:
                return self.ignore()
        else:
            return self.ignore()
