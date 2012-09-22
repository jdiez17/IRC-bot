from functools import wraps

def admincommand(fn):
    @wraps(fn)
    def wrapper(self, msg, cmd, user, arg):
        if not self.is_admin(user):
            return self.send_message("Permission denied.")
        else:
            try:
                return fn(self, msg, cmd, user, arg)
            except Exception, e:
                print str(e)

    return wrapper
