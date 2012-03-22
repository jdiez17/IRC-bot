from module import Module

class Test(Module):
	def __init__(self):
		self.modname = "TestMod"
		
	def parse(self, msg, cmd, user, arg):
		if cmd == ".test":
			msg = "hell yes."
			return self.send_message(msg)
			
		if cmd == ".utftest":
			try:
				string = arg[0].decode("utf-8")
				return self.send_message("decoded with utf-8 codec")
			except:
				return self.send_message("unable to decode with utf-8 codec")
			return 
			
		else:
			return self.ignore()