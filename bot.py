# -*- coding: utf-8 -*-

import ConfigParser, os
import socket
import sys
import time


class IRCBot():
	def __init__(self):
		self.nick = ""
		self.password = ""
		self.home_channel = ""
		
		self.s = None
		self.modules = []
		self.config = None
		
		self.admins = []
		self.transport = ""

		self.locked = False
		self.lock_ended = False
		
	def log(self, line):
		print line
		
		file = open(self.config.get('log', 'path'), 'a')
		file.write("[" + str(time.time()) + "] " + line + "\n")
		
		file.close()
		
	def lineReceived(self, line):
		self.parse(line)
			
	def connect(self, server, port):
		self.s = socket.socket()
		self.s.connect((server, port))
		self.s.send("USER "+ self.nick +" "+ self.nick +" "+ self.nick +" :ariobot\n") 
		self.s.send("NICK "+ self.nick +"\r\n")
		
		print "Loaded modules: "
		for module in self.modules:
			print "- " + module.modname
		
		time.sleep(2)
		self.main_loop()
		
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
		print "III " + str(response)
		if response == None:
			print "!!! Malfunction -> " + str(module)
		elif response['accepted'] == -1:
			print "!!! Malfunction (class 2) -> " + response['module']
		elif response['accepted'] == True:
			if not self.locked or bypass_lock:
				if response.has_key('reconnect'):
					self.transport.loseConnection()
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
			try:
				try:
					msg = line.split(":", 2)[2]
				except:
					return
				cmd = msg.split(" ")[0]
				user = line.split(":")[1].split("!")[0]
				arg = msg.split(" ")[1:]
			
				if "PRIVMSG " + self.nick in line:
					user = "**" + user # **user denotes private message.
			
				self.user_cmd(msg, cmd, user, arg)
			except:
				raise
				print "!!! " + line
				print "!!! Possible bug."
		
		else:
			for module in self.modules:
				if "parse_raw" in dir(module):
					response = module.parse_raw(line)
				
					self.__parse_response(response, module) # no return, we don't want to end the chain here.
				
	
	def user_cmd(self, msg, cmd, user, arg):
		for module in self.modules:
			if "parse" in dir(module):
				response = module.parse(msg, cmd, user, arg)
				
				resp_resp = self.__parse_response(response, module)
				if resp_resp == True:
					return True
	
	def set_config(self, config):
		self.config = config
		
		self.nick = config.get('core', 'nick')
		self.admins = [config.get('core', 'admin'), self.nick]
		self.home_channel = config.get('core', 'home_channel')
		self.password = config.get('core', 'password')
	
	def load_module(self, module):
		module.set_admins(self.admins)
		module.set_nick(self.nick)
		module.set_config(self.config)
		self.modules.append(module)
		
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
							print "III Ignoring '" + lines + "'"
				else:
					lines = lines.split("\r\n")
					for line in lines:
						if line.strip(): # line is not empty
							self.log(">>> " + line)
							self.lineReceived(line)
						
			except(KeyboardInterrupt, SystemExit):
				self.__send_raw("QUIT :CTRL-c")
				sys.exit()
	
if __name__ == '__main__':
	from modules.test import Test
	from modules.toalla_r import Toalla_R
	from modules.toalla import Toalla
	from modules.admincommands import AdminCommands
	from modules.annoying import Annoying
	from modules.twirc import TwIRC
	from modules.qdb import QDB2
	from modules.antitoalla import AntiToalla
	from modules.useful import Useful
	from modules.texts import Texts
	
	config = ConfigParser.ConfigParser()
	config.readfp(open('config.ini'))
	
	bot = IRCBot()
	
	bot.set_config(config)
	bot.load_module(Test())
	bot.load_module(Useful())
	bot.load_module(Toalla_R())
	bot.load_module(Toalla())
	bot.load_module(AdminCommands())
	bot.load_module(Annoying())
	bot.load_module(TwIRC())
	bot.load_module(QDB2())
	bot.load_module(AntiToalla())
	bot.load_module(Texts())
	
	bot.connect(config.get('core', 'server'), int(config.get('core', 'port')))
