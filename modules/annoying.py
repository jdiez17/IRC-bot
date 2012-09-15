from module import Module

class Annoying(Module):
    def __init__(self):
        self.modname = "Annoying bot"
        
    def parse_custom(self, msg, cmd, user, arg):
        if " ok?" in msg or "ok?" == cmd:
            return self.send_message("ok")
        else:
            return self.ignore()
            
    def parse_raw(self, line):
        return self.ignore() # disabled

        if "JOIN " in line:
            user = line.split(":")[1].split("!")[0]
            if user == self.nick or user[:1] == "#":
                return self.ignore()
            
            return self.send_message("hola " + user + " que tal?")
        else:
            return self.ignore()
