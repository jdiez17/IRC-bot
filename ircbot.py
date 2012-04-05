# -*- coding: utf-8 -*-
import os, socket, sys, time, inspect, logging, logging.handlers

class IRCBot(object):
	def __init__(self):
		self.nick = ""
		self.password = ""
		self.home_channel = ""
		
		self.s = None
		self.tmp_modules = []
		self.modules = dict()
		self.__seqno = 0
		self.config = None
		self.logger = None
		
		self.admins = []
		self.transport = ""

		self.locked = False
		self.lock_ended = False
		
	def log(self, line):
		print line
		self.logger.debug(line)
		
	def log_info(self, line):
		print line
		self.logger.info(line)
	
	def log_warn(self, line):
		print line
		self.logger.warning(line)
	
	def lineReceived(self, line):
		self.parse(line)
			
	def connect(self, server, port):
		self.logger = logging.getLogger('bot')
		self.logger.setLevel(logging.DEBUG)
		handler = logging.handlers.TimedRotatingFileHandler(self.config.get('log', 'path') + 'bot.log', self.config.get('log', 'rollover'))
		self.logger.addHandler(handler)
	
		self.s = socket.socket()
		self.s.connect((server, port))
		self.s.send("USER "+ self.nick +" "+ self.nick +" "+ self.nick +" :ariobot\n") 
		self.s.send("NICK "+ self.nick +"\r\n")
		
		print "Loaded modules: "
		for seqno in self.modules:
			print "- " + self.modules[seqno].modname + " (" + str(seqno) + ")"
		
		time.sleep(2)
		self.main_loop()
		sys.exit() # should never be reached
		
	def __send_raw(self, cmd):
		self.log("<<< " + cmd)
		try:
			self.s.send(cmd.encode("utf-8") + "\n")
		except:
			self.s.send(cmd + "\n")
		
	def __send(self, msg, override = False, channel_snd = "placeholder"):
		if channel_snd == "placeholder":
			channel_snd = self.home_channel
		
		self.__send_raw("PRIVMSG " + channel_snd + " :" + msg)
		
	def send(self, msg):
		return self.__send(msg)
	
	def __parse_response(self, response, module, bypass_lock = False):				
		self.log_info("III " + str(response))
		if response == None:
			self.log_warn("!!! Malfunction -> " + str(module))
		elif response['accepted'] == -1:
			self.log_warn("!!! Malfunction (class 2) -> " + response['module'])
		elif response['accepted'] == True:
			if not self.locked or bypass_lock:
				if response.has_key('ctcp_command'):
					self.__send_raw("NOTICE " + response['ctcp_who'] + " :" + '\x01' + response['ctcp_command'] + " " + response['ctcp_response'] + '\x01') 
				if response.has_key('special_request'):
					self.__handle_special_request(response)
				if response.has_key('reconnect'):
					sys.exit()
				if response.has_key('acquire_lock'):
					self.locked = True
					self.lock_ended = False
					return
				if response.has_key('release_lock'):
					self.lock_ended = True
					return
				if response.has_key('actions'):
					for action in response['actions']:
						time.sleep(0.5)
						self.__parse_response(action, response['module'], True)
				if response.has_key('message'):
					self.__send(response['message'])
				if response.has_key('raw_message'):
					self.__send_raw(response['raw_message'])
				if response.has_key('recursion'):
					if response['recursion'] == True:
						time.sleep(0.5)
						self.user_cmd("", response['cmd'], response['user'], response['arg'])
				return True
	
	def parse(self, line):
		if "PING :" in line:
			pingresponse = line.split(":", 1)[1]
			self.__send_raw("PONG :" + pingresponse + "\r")
			
		elif "NOTICE AUTH :*** You need to send your password. Try /quote PASS <username>:<password>" in line:
			self.__send_raw("PASS " + self.password)
			
		elif "376 " + self.nick in line:
			self.__send_raw("JOIN "+ self.home_channel +"\r\n") 
			
		elif "PRIVMSG" in line:
			if '\x01' in line: # ctcp
				user = line.split(":")[1].split(" ")[0]
				self.user_ctcp(user, line)
			else:
				try:
					try:
						msg = line.split(":", 2)[2]
					except:
						return
					cmd = msg.split(" ")[0]
					#user = line.split(":")[1].split("!")[0]
					user = line.split(":")[1].split(" ")[0]
					arg = msg.split(" ")[1:]
				
					if "PRIVMSG " + self.nick in line:
						user = "**" + user # **user denotes private message.
				
					self.user_cmd(msg, cmd, user, arg)
				except:
					raise
					self.log_warn("!!! " + line)
					self.log_warn("!!! Possible bug.")
		
		else:
			self.raw_user_cmd(line)
				
	
	def user_ctcp(self, user, line):
		for seq in self.modules:
			module = self.modules[seq]
			
			if "parse_ctcp" in dir(module):
				response = module.parse_ctcp(user, line)
				self.__parse_response(response, module)
	
	def raw_user_cmd(self, line):
		for seq in self.modules:
			module = self.modules[seq]
			
			if "parse_raw" in dir(module):
				response = module.parse_raw(line)
			
				self.__parse_response(response, module) 
				
	def user_cmd(self, msg, cmd, user, arg):
		for seq in self.modules:
			module = self.modules[seq]
			
			if "parse" in dir(module):
				try:
					response = module.parse(msg, cmd, user, arg)
				except:
					self.logger.exception("!!! Exception in module code.")

				resp_resp = self.__parse_response(response, module, module.is_admin(module.get_username(user)))
				if resp_resp == True:
					return True
	
	def __handle_special_request(self, response):
		if response['special_request'] == 'get_modules':
			modules = [] 
			for seq in self.modules:
				modules.append(self.modules[seq].modname)
			
			self.__parse_response(response['callback'](modules), response['module'])
		
		if response['special_request'] == 'get_commands':
			try: 
				commands = []
				for seq in self.modules:
					if self.modules[seq].modname == response['extra'][0]:
						for command in self.modules[seq].commands:
							commands.append(command)
				
				self.__parse_response(response['callback'](commands), response['module'])
			except:
				self.__parse_response(response['callback']([]), response['module'])
	
	def set_config(self, config):
		self.config = config
		
		self.nick = config.get('core', 'nick')
		self.admins = [config.get('core', 'admin'), self.nick]
		self.home_channel = config.get('core', 'home_channel')
		self.password = config.get('core', 'password')
	
	def module_with_priority(self, priority):
		howmany = 0
	
		for module in self.tmp_modules:
			if "priority" in dir(module):
				if module.priority == priority:
					howmany += 1
		
		return False if howmany == 0 else howmany
	
	def get_next_seqno(self):
		proposed_seqno = 0
		
		while proposed_seqno == 0:
			proposed_seqno = self.__seqno if not self.module_with_priority(self.__seqno) else 0
			if proposed_seqno == 0:
				self.__seqno += 1
		return proposed_seqno
	
	def load_module(self, module):
		module.set_admins(self.admins)
		module.set_nick(self.nick)
		module.set_config(self.config)
		
		self.tmp_modules.append(module)
		
	def check_repeated_priorities(self):
		print "check_repeated_priorities"
	
		for module in self.tmp_modules:
			if "priority" in dir(module):
				if self.module_with_priority(module.priority) > 1:
					module.priority += 1
					
					self.check_repeated_priorities() # here be recursion
	
	def end_load_modules(self):
		self.check_repeated_priorities()
	
		for module in self.tmp_modules:
			self.__seqno += 1
			seqno = 0
	
			if "priority" in dir(module):
				seqno = module.priority
			else:
				seqno = self.get_next_seqno()
			
			while self.modules.has_key(seqno):
				seqno += 1
				self.__seqno += 1
					
			self.modules[seqno] = module
		
	def main_loop(self):
		while 1:
			try:
				time1 = time.time()
				lines = self.s.recv(4092)
				time2 = time.time()
				
				if self.lock_ended:
						self.lock_ended = False
						self.locked = False
						
						if  (time2 - time1 > 1): # lol fix this crap
							lines = lines.split("\r\n")
							for line in lines:
								if line.strip(): # line is not empty
									self.log(">>> " + line)
									self.lineReceived(line)
						else:
							self.log_info("III Ignoring '" + lines + "'")
				else:
					lines = lines.split("\r\n")
					for line in lines:
						if line.strip(): # line is not empty
							self.log(">>> " + line)
							self.lineReceived(line)
						
			except(KeyboardInterrupt, SystemExit):
				self.__send_raw("QUIT :CTRL-c")
				sys.exit()
	