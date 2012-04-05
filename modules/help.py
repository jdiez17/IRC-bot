from module import Module
from response.response import Response

class Help(Module):
	def __init__(self):
		self.modname = "Help"
		self.commands = dict()
		
		self.add_command(".help", self.get_help)
		
	def get_help(self, msg, cmd, user, arg): 
		module = " ".join(arg)
		
		if module:
			return self.special_request("get_commands", self.handle_commands, [module])
		else:
			return self.special_request("get_modules", self.handle_modules)
	
	def handle_commands(self, commands):
		return self.send_message("Comandos disponibles: " + ", ".join(commands))
	
	def handle_modules(self, modules):
		response = Response()
		
		response.add_action(self.send_message("Módulos disponibles: " + ', '.join(modules)))
		response.add_action(self.send_message("Escribe .help <module> para ver los comandos de un módulo."))
		
		return self.multiple_response(response.generate_response())
		