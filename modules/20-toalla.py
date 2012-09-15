from module import Module
import time
import random

class Toalla(Module):
    def __init__(self):
        self.modname = "ToallaBot"
        self.last_toalla = 0
        self.toalla_timeout = 5
        self.priority = 2
        self.commands = dict()
        
        self.add_command(".toalla", self.toalla)
        
    def toalla(self, msg, cmd, user, arg): 
        toallas = open('/usr/share/toalla.txt')
        override = self.is_admin(user)
        diff = time.time() - self.last_toalla
        
        if diff < self.toalla_timeout and not override:
            self.ignore()
        
        toa_list = [] 
        
        times = 1
        nick = ' '.join(arg[0:]).strip()

        if nick[:1] == "@":
            tollatweet = True
        else:
            tollatweet = False
            
        if self.is_admin(nick):
            return self.ignore()

        for toalla in toallas:
            this_toalla = toalla.replace("\n", "")
            this_toalla = this_toalla.replace("$1-", nick)
            this_toalla = this_toalla.replace("$me", self.nick)
            this_toalla = this_toalla.replace("$network", "#fearnode") # fix hardcode

            toa_list.append(this_toalla)

        the_toalla = random.choice(toa_list)
        while "$nick" in the_toalla or (len(the_toalla) > 140 and tollatweet):
            the_toalla = random.choice(toa_list)
            
        if tollatweet:
            return self.recursion_no_message(".tweet", user, [the_toalla])
        else:
            return self.send_message(the_toalla)
            
        self.last_toalla = time.time()
        
    def parse_custom(self, msg, cmd, user, arg):
        if self.nick.lower() in cmd.lower() and not self.is_privmsg(user):
            return self.recursion_no_message(".toalla", user, [self.get_username(user)])
    