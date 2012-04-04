from module import Module
import random

class Useful(Module):
	def __init__(self):
		self.modname = "Useful Bot"
		self.priority = 1
		
	def parse_ctcp(self, user, line):
		if '\x01' + "VERSION" + '\x01' in line:
			return self.send_ctcp(self.get_username(user), "VERSION", self.config.get('core', 'version'))
			
	def parse_custom(self, msg, cmd, user, arg):
		if self.nick in cmd and " o " in msg and "?" in msg:
			question = msg.replace(cmd, '')
			question = question.replace('?', '')
			
			possibilities = question.split(" o ")
			choice = possibilities[random.randint(0, len(possibilities) -1)]
			
			if choice:
				return self.send_message(self.get_username(user) + ": " + choice)