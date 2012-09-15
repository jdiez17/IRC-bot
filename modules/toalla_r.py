from module import Module

import time
import random
import re

class Toalla_R(Module):
    def __init__(self):
        self.modname = "Toalla Regular Expressions"
        self.last_toalla = 0
        self.toalla_timeout = 5
        self.priority = 3

    def parse(self, msg, cmd, user, arg):
        if ".toalla_r" == cmd:
            toallas = open('/usr/share/toalla.txt')
            override = self.is_admin(user)
            diff = time.time() - self.last_toalla
            
            if diff < self.toalla_timeout and not override:
                self.ignore()
            
            toa_list = [] 
            
            times = 1
            nick = ' '.join(arg[1:]).strip()
            
            if nick[:1] == "@":
                times = 1
                tollatweet = True
            else:
                tollatweet = False
                
            if self.is_admin(nick):
                return self.send_message("No.")

            found_toalla = False
            matching_toallas = []
                
            for toalla in toallas:
                this_toalla = toalla.replace("\n", "")
                this_toalla = this_toalla.replace("$1-", nick)
                this_toalla = this_toalla.replace("$me", self.nick)
                this_toalla = this_toalla.replace("$network", "#fearnode") # fix hardcode               
                toa_list.append(this_toalla)
                
                try:
                    if re.search(arg[0], this_toalla) != None:
                        matching_toallas.append(this_toalla)
                        found_toalla = True
                except:
                    return self.send_message("Mira, me cago en tu madre, "+user)
                    
            if not found_toalla:
                the_toalla = random.choice(toa_list)
            else:
                the_toalla = random.choice(matching_toallas)
            
            while "$nick" in the_toalla or (len(the_toalla) > 140 and tollatweet):
                the_toalla = random.choice(toa_list)
                
            if tollatweet:
                return self.recursion_no_message(".tweet", user, [the_toalla])
            else:
                if times > 1:
                    return self.recursion_with_message(the_toalla, ".toalla", user, [times-1, nick])
                else:
                    return self.send_message(the_toalla)
            self.last_toalla = time.time()
        else:
            return self.ignore()