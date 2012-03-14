# -*- coding: utf-8 -*-

import ConfigParser, os
import socket
import sys
import time
from multiprocessing import Process, Pipe
from twisted.protocols import basic
from twisted.internet import stdio, reactor
from twisted.internet.protocol import ClientFactory


class IRCBot(basic.LineReceiver):
	def __init__(self):
		self.nick = ""
		self.password = ""
		self.home_channel = ""
		
		self.modules = []
		self.config = None
		
		self.admins = []
		self.transport = ""

		
	def lineReceived(self, line):
		if line.strip():
			print ">>> " + line
			self.parse(line)
			
	def connectionMade(self):
		self.transport.write("USER "+ self.nick +" "+ self.nick +" "+ self.nick +" :ariobot\n") 
		self.transport.write("NICK "+ self.nick +"\r\n")
		
		print "Loaded modules: "
		for module in self.modules:
			print "- " + module.modname
		
	def __send_raw(self, cmd):
		print "<<< " + cmd
		self.transport.write(cmd.encode("utf-8") + "\n")
		
	def __send(self, msg, override = False, channel_snd = "placeholder"):
		if channel_snd == "placeholder":
			channel_snd = self.home_channel
			
		self.__send_raw("PRIVMSG " + channel_snd + " :" + msg)
		
	def send(self, msg):
		return self.__send(msg)
	
	def __parse_response(self, response, module):				
		print "III " + str(response)
		if response == None:
			print "!!! Malfunction -> " + str(module)
		elif response['accepted'] == -1:
			print "!!! Malfunction (class 2) -> " + response['module']
		elif response['accepted'] == True:
			if response.has_key('reconnect'):
				self.transport.loseConnection()
			if response.has_key('actions'):
				for action in response['actions']:
					self.__parse_response(action, response['module'])
			if response.has_key('message'):
				self.__send(response['message'])
			if response.has_key('raw_message'):
				self.__send_raw(response['raw_message'])
			if response.has_key('recursion'):
				if response['recursion'] == True:
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
		
class IRCBotFactory(ClientFactory):
	def __init__(self, config):
		self.config = config
		
	def buildProtocol(self, addr):
		bot = IRCBot()
	
		bot.set_config(config)
		bot.load_module(Test())
		bot.load_module(Toalla_R())
		bot.load_module(Toalla())
		bot.load_module(AdminCommands())
		bot.load_module(Annoying())
		bot.load_module(TwIRC())
		bot.load_module(QDB2())
		bot.load_module(AntiToalla())
		
		return bot
		
	def clientConnectionLost(self, connector, reason):
		connector.connect()
	
if __name__ == '__main__':
	from modules.test import Test
	from modules.toalla_r import Toalla_R
	from modules.toalla import Toalla
	from modules.admincommands import AdminCommands
	from modules.annoying import Annoying
	from modules.twirc import TwIRC
	from modules.qdb import QDB2
	from modules.antitoalla import AntiToalla
	
	config = ConfigParser.ConfigParser()
	config.readfp(open('config.ini'))
		
	reactor.connectTCP(config.get('core', 'server'), int(config.get('core', 'port')), IRCBotFactory(config))
	reactor.run()
