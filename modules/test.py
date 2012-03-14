from module import Module

class Test(Module):
	def __init__(self):
		self.modname = "TestMod"
		
	def parse(self, msg, cmd, user, arg):
		if cmd == ".test":
			msg = "hell yes."
			return self.send_message(msg)
		else:
			return self.ignore()