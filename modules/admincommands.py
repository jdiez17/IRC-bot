from module import Module
import sys

class AdminCommands(Module):
	def __init__(self):
		self.modname = "Admin Commands"
		
	def parse_raw(self, line):
		if "ERROR :Closing Link:" in line:
			return self.reconnect()
			
		if "INVITE " + self.nick in line:
			return self.send_raw_message("JOIN " + "#fearnode") # fix hardcode
		else:
			return self.ignore()
	
	def parse(self, msg, cmd, user, arg):
		if not self.is_admin(user):
			return self.ignore()
			
		if cmd == ".rehash":
			return self.reconnect()
			
		if cmd == ".parrot":
			msg = msg.replace(cmd + " ", "")
			return self.send_message(msg)
			
		if cmd == ".join":
			return self.send_raw_message("JOIN " + arg[0])
			
		else:
			return self.ignore()
		