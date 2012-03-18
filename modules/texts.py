from module import Module
from response.response import Response
import os

class Texts(Module):
	def __init__(self):
		self.modname = "Texts reader"
		self.path = ""
		
	def initialize(self):
		self.path = self.config.get('texts', 'path')
		
	def parse(self, msg, cmd, user, arg):
		if cmd == ".ltext":
			texts = os.listdir(self.path)
			return self.send_message(', '.join(texts))
		if cmd == ".text":
			try:
				if "." in arg[0]:
					return self.send_message("A hackear a tu casa.")
			except:
				return self.send_message("Tu puta madre.")
			
			try:
				file = open(self.path + arg[0]).readlines()
			except:
				return self.send_message("Ese texto no existe.")
				
			response = Response()
			
			for line in file:
				response.add_action(self.send_message(line))
				
			return self.multiple_response(response.generate_response())
		else:
			return self.ignore()