from module import Module

class Test(Module):
    def __init__(self):
        self.modname = "TestMod"
        self.commands = dict()
        
        self.add_command(".test", self.test)
    
    def test(self, msg, cmd, user, arg):
        return self.send_message("hell yes")