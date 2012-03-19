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
		self.qdb_secret = ""
		self.quote_users = {}
		self.initialized = False
		
	def initialize(self):
		if self.initialized: return
		
		self.qdb_secret = self.config.get('qdb', 'password')
		self.initialized = True
		
	def parse(self, msg, cmd, user, arg):
		if cmd == ".read":
			response = Response()
			try:
				result = requests.get(self.qdb_api_read % arg[0])
			except:
				return self.send_message("Tu puta madre.")
			try:
				result = json.loads(result.content)
			
				if result['results'].has_key('success'):
					if result['results']['success'] == 1:
						quote = result['results']['data']['text'].split("\n")
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
				response.add_action(self.send_message('wodim, arregla el qdb.'))
				
			return self.multiple_response(response.generate_response())
		if cmd == ".password":
			m = hashlib.md5()
			m.update(date.today().strftime("%d/%m/%Y") + self.qdb_secret)
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
			m = hashlib.md5()
			m.update(date.today().strftime("%d/%m/%Y") + self.qdb_secret)
			password = m.hexdigest()[:8]
			
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
			r = requests.post(self.qdb_api_post % password, data=payload)
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
