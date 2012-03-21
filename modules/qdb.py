from module import Module
from response.response import Response

import hashlib
import requests
import json
from datetime import date

class QDB2(Module):
	def __init__(self):
		self.modname = "Fearnode QDB"
		
		self.qdb_api_post = "http://qdb.vortigaunt.net/api/send/%s"
		self.qdb_login = "http://qdb.vortigaunt.net/login/%s"
		self.qdb_api_read = "http://qdb.vortigaunt.net/api/read/%s"
		self.qdb_api_search = "http://qdb.vortigaunt.net/api/search/%s"
		
		self.qdb_secret = ""
		self.qdb_password = ""
		self.quote_users = {}
		self.initialized = False
		
	def initialize(self):
		if self.initialized: return
		
		self.qdb_secret = self.config.get('qdb', 'apikey')
		self.qdb_password = self.config.get('qdb', 'password')
		self.initialized = True
		
	def parse(self, msg, cmd, user, arg):
		if cmd == ".search":
			response = Response()
			try:
				result = requests.post(self.qdb_api_search % self.qdb_secret, data={'criteria': ' '.join(arg), 'page_size': 10})
			except:
				return self.send_message("Tu puta madre.")
			
			try:
				result = json.loads(result.content)
				
				if result['results'].has_key('success'):
					if result['results']['success'] == 1:
						if result['results']['count'] == 0:
							return self.send_message("No quotes matching that criteria found.")
						else:
							for quote in result['results']['data']:
								firstline = quote['text'].split("\n")[0]
								response.add_action(self.send_message(quote['permaid'] + " - " + quote['nick'] + ": '" + firstline + "'"))
							
							response.add_action(self.send_message("Escribe .read <id> para leer el quote completo."))
								
					else:
						return self.send_message("Algo se ha roto. (dunno lol)")
			except:
				raise
				return self.send_message("wodim, arregla el qdb.")
				
			return self.multiple_response(response.generate_response())
		if cmd == ".read":
			response = Response()
			try:
				result = requests.post(self.qdb_api_read % self.qdb_secret, data={'permaid': arg[0]})
			except:
				return self.send_message("Tu puta madre.")
			try:
				result = json.loads(result.content)
			
				if result['results'].has_key('success'):
					if result['results']['success'] == 1:
						quote = result['results']['data']['text'].split("\n")
						response.add_action(self.send_message('Enviado por ' + result['results']['data']['nick'] + ':'))
						
						for line in quote:
							if "\r" in line or "\n" in line:	
								for subline in line.split("\r\n"):
									response.add_action(self.send_message(subline))
							else:
								response.add_action(self.send_message(line))
					else:
						problem = {'hidden_quote': 'The quote is hidden.', 'no_such_quote': 'No such quote exists.'}[result['results']['error']]
						response.add_action(self.send_message("Error: " + problem))
			except:
				return self.send_message('wodim, arregla el qdb.')
				
			return self.multiple_response(response.generate_response())
		if cmd == ".password":
			m = hashlib.md5()
			m.update(date.today().strftime("%d/%m/%Y") + self.qdb_password)
			password = m.hexdigest()[:8]
			
			return self.send_message(self.qdb_login % password)
		if msg[:5] == ".send":
			if user[:2] == "**":
				user = user[2:].strip()
			else:
				return self.ignore()
				
			if user not in self.quote_users:
					return self.send_raw_message("PRIVMSG " + user + " :Pega un quote antes.")
				
			quote = ""
			
			if(msg[:13] == ".send_private"):
				comment = msg[13:]
				private = 1
			else:
				comment = msg[5:]
				private = 0
				
			for line in self.quote_users[user]:
				try:
					quote = quote + "\n" + unicode(line, "cp1252").encode("utf-8")
				except:
					return self.send_message("Pues va a ser que no.")
					
			
			if quote == "":
				return self.ignore()
			
			payload = {'nick': user + ' (bot)', 'text': quote, 'comment': comment, 'hidden': private}
			r = requests.post(self.qdb_api_post % self.qdb_secret, data=payload)
			try:
				r = json.loads(r.content)
			except:
				return self.send_message('wodim, arregla el qdb.')
			
			self.quote_users[user] = []
			return self.send_message(r['results']['url'] + " " + comment + " (" + user + ")")
		elif cmd == ".cancel" and user[:2] == "**":
			user = user[2:]
			
			self.quote_users[user] = []
			return self.send_raw_message("PRIVMSG " + user + " :Hecho.")
		elif user[:2] == "**":
			user = user[2:]
			
			if user in self.quote_users:
				if self.quote_users[user] == []:
					send = True
				else:
					send = False
				
				try:
					self.quote_users[user].append(msg.encode("utf-8"))
				except:
					self.quote_users[user].append(msg)
				
				if send:
					return self.send_raw_message("PRIVMSG " + user + " :Escribe .send <comentario> cuando termines, .send_private <comentario> para enviar quote privado, o .cancel para cancelar.")
				else:
					return self.accept()
			else:
				self.quote_users[user] = [msg]
				return self.send_raw_message("PRIVMSG " + user + " :Escribe .send <comentario> cuando termines, .send_private <comentario> para enviar quote privado, o .cancel para cancelar.")

		else:
			return self.ignore()
