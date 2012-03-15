class Module():
	def __init__(self):
		self.modname = "unnamed_mod"
		self.admins = []
		self.nick = ""
		self.config = None
		
	def set_admins(self, admins):
		self.admins = admins
	
	def set_nick(self, nick):
		self.nick = nick
		
	def set_config(self, config):
		self.config = config
		
		if "initialize" in dir(self):
			self.initialize()
			
	def __malfunction(self):
		return {'accepted': -1, 'module': self.modname}
		
	def generate_response(self, accepted = True, message = "", raw_message = "", recursion = False, r_cmd = "", r_user = "", r_arg = ""):
		response = {}
		
		if len(message) > 1 and len(raw_message) > 1:
			print "EEE message and raw_message collision"
			return self.__malfunction()
		
		if len(message) > 1 and not accepted:
			print "EEE message but not accepted"
			return self.__malfunction()
		
		if len(raw_message) > 1 and not accepted:
			print "EEE raw_message but not accepted"
			return self.__malfunction()
		
		if message:
			response['message'] = message
		if raw_message:
			response['raw_message'] = raw_message
		if recursion:
			response['cmd'] = r_cmd
			response['user'] = r_user
			response['arg']  = r_arg

		response['accepted'] = accepted
		response['recursion'] = recursion
		response['module'] = self.modname
		
		return response
		
	def send_message(self, msg):
		return self.generate_response(True, msg)
	
	def send_raw_message(self, raw_msg):
		return self.generate_response(True, "", raw_msg)
	
	def recursion_no_message(self, cmd, user, arg):
		return self.generate_response(True, "", "", True, cmd, user, arg)
		
	def recursion_with_message(self, msg, cmd, user, arg):
		return self.generate_response(True, msg, "", True, cmd, user, arg)
		
	def recursion_with_raw_message(self, raw_msg, cmd, user, arg):
		return self.generate_response(True, "", raw_msg, True, cmd, user, arg)
		
	def reconnect(self):
		return {'reconnect': True, 'accepted': True}
	def ignore(self):
		return self.generate_response(False)
		
	def accept(self):
		return self.generate_response(True)
	
	def multiple_response(self, actions):
		response = {}
		
		response['accepted'] = True
		response['module'] = self.modname
		response['actions'] = actions
		
		return response
	
	def async_send_message(self, message):
		print "!!! !!! ASYNC MESSAGE " + message
		self.parent.send("lol")
	
	def is_admin(self, user):
		if user[:2] == "**":
			user = user[2:]
		for admin in self.admins:
			if admin in user and user != self.nick:
				return True
				
		return False