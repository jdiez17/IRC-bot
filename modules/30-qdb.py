from module import Module
from response.response import Response

import hashlib
import requests
import json
from datetime import date

class QDB2(Module):
    def __init__(self):
        self.modname = "Fearnode QDB"


        self.qdb_base = "http://qdb.fearnode.net/" 

        self.qdb_api_post = self.qdb_base + "api/send/%s"
        self.qdb_login = self.qdb_base + "login/%s"
        self.qdb_api_read = self.qdb_base + "api/read/%s"
        self.qdb_api_search = self.qdb_base + "api/search/%s"
        self.qdb_api_delete = self.qdb_base + "api/delete/%s"
        self.qdb_api_topic = self.qdb_base + "api/topic/%s"

        self.qdb_secret = ""
        self.qdb_password = ""
        self.quote_users = {}
        self.initialized = False
        self.priority = 4
        
        self.commands = dict()
        self.add_command(".delete", self.delete)
        self.add_command(".search", self.search)
        self.add_command(".read", self.read)
        self.add_command(".send", self.send)
        self.add_command(".send_private", self.send)
        self.add_command(".cancel", self.cancel)
        self.add_command(".password", self.password)
        
    def initialize(self):
        if self.initialized: return
        
        self.qdb_secret = self.config.get('qdb', 'apikey')
        self.qdb_password = self.config.get('qdb', 'password')
        self.initialized = True
        
    def delete(self, msg, cmd, user, arg):
        try:
            result = requests.post(self.qdb_api_read % self.qdb_secret, data={'permaid': arg[0]})
        except:
            return self.send_message("Tu puta madre.")
        
        try:
            result = json.loads(result.content)
        except:
            return self.send_message("wodim, arregla el qdb.")
        
        try:
            if result['results']['data']['ip'] == self.get_vip(user):
                try:
                    result = requests.post(self.qdb_api_delete % self.qdb_secret, data={'permaid': arg[0]})
                    result = json.loads(result.content)
                    
                    if result['results']['success'] == 1:
                        return self.send_message("Hecho.")
                    else:
                        return self.send_message("No hecho. (qdb)")
                except:
                    return self.send_message("Tu puta madre. " + result.content)
            else:
                return self.send_message("No autorizado.")
        except:
            return self.send_message("Ese ID no existe.")
        
    def search(self, msg, cmd, user, arg): 
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
                            firstline = quote['excerpt']
                            response.add_action(self.send_message(quote['permaid'] + " - " + quote['nick'] + ": '" + firstline + "'"))
                        
                        response.add_action(self.send_message("Escribe .read <id> para leer el quote completo."))
                            
                else:
                    return self.send_message("Algo se ha roto. (dunno lol)")
        except:
            raise
            return self.send_message("wodim, arregla el qdb.")
            
        return self.multiple_response(response.generate_response())
        
    def read(self, msg, cmd, user, arg):
        response = Response()
        try:
            result = requests.post(self.qdb_api_read % self.qdb_secret, data={'permaid': arg[0]})
        except:
            return self.send_message("Tu puta madre.")
        try:
            result = json.loads(result.content)
        
            if result['results'].has_key('success'):
                if result['results']['success'] == 1:
                    if result['results']['data']['status'] == "deleted":
                        return self.send_message("Quote is deleted.")
                    else:
                        quote = result['results']['data']['text'].split("\n")
                        response.add_action(self.send_message('Enviado por ' + result['results']['data']['nick'] + ' (' + result['results']['data']['date'] + '):'))
                        
                        for line in quote:
                            if "\r" in line or "\n" in line:    
                                for subline in line.split("\r\n"):
                                    response.add_action(self.send_message(subline))
                            else:
                                response.add_action(self.send_message(line))
                                
                        if result['results']['data']['comment']:
                            comment = result['results']['data']['comment']
                            dashes_length = int((40 - len(comment)) / 2) # little decorator
                            response.add_action(self.send_message(("-" * dashes_length) + comment + ("-" * dashes_length)))
                else:
                    problem = {'hidden_quote': 'The quote is hidden.', 'no_such_quote': 'No such quote exists.'}[result['results']['error']]
                    response.add_action(self.send_message("Error: " + problem))
        except:
            return self.send_message('wodim, arregla el qdb.')
            
        return self.multiple_response(response.generate_response())
    
    def password(self, msg, cmd, user, arg):
        m = hashlib.md5()
        m.update(date.today().strftime("%d/%m/%Y") + self.qdb_secret)
        password = m.hexdigest()[:8]
        
        return self.send_message(self.qdb_login % password)
        
    def send(self, msg, cmd, user, arg):
        if msg[:5] == ".send":
            if user[:2] == "**":
                user = user[2:].strip()
            else:
                return self.ignore()
                
            if user not in self.quote_users:
                    return self.send_raw_message("PRIVMSG " + self.get_username(user) + " :Pega un quote antes.")
                
            quote = ""
            
            if(msg[:13] == ".send_private"):
                comment = msg[13:]
                private = 1
            else:
                comment = msg[5:]
                private = 0
                
            for line in self.quote_users[user]:
                quote = quote + "\n" + unicode(line)
                    
            
            if quote == "":
                return self.ignore()
            
            payload = {'nick': self.get_username(user) + ' (bot)', 'text': quote, 'comment': comment, 'hidden': private, 'ip': self.get_vip(user)}
            r = requests.post(self.qdb_api_post % self.qdb_secret, data=payload)
            try:
                r = json.loads(r.content)
            except:
                #return self.send_message('wodim, arregla el qdb.')
                raise
            
            self.quote_users[user] = []
            return self.generate_response()
             
    def cancel(self, msg, cmd, user, arg):
        if user[:2] == "**":
            user = user[2:]
            
            self.quote_users[user] = []
            return self.send_raw_message("PRIVMSG " + self.get_username(user) + " :Hecho.")
            
        
    def parse_custom(self, msg, cmd, user, arg):
        if user[:2] == "**":
            user = user[2:]
            
            if user in self.quote_users:
                if self.quote_users[user] == []:
                    send = True
                else:
                    send = False
    
                self.quote_users[user].append(msg)
                
                if send:
                    return self.send_raw_message("PRIVMSG " + self.get_username(user) + " :Escribe .send <comentario> cuando termines, .send_private <comentario> para enviar quote privado, o .cancel para cancelar.")
                else:
                    return self.accept()
            else:
                self.quote_users[user] = [msg]
                return self.send_raw_message("PRIVMSG " + self.get_username(user) + " :Escribe .send <comentario> cuando termines, .send_private <comentario> para enviar quote privado, o .cancel para cancelar.")

    def parse_raw(self, line):
        if "TOPIC " in line:
            user = line.split(":")[1].split("!")[0]
            topic = ':'.join(line.split(":")[2:])

            payload = {'nick': user, 'topic': topic}
            requests.post(self.qdb_api_topic % self.qdb_secret, data=payload)
