class Response():
    def __init__(self):
        self.actions = [{'acquire_lock': True, 'accepted': True}]
    
    def add_action(self, action):
        self.actions.append(action)
    
    def generate_response(self):
        self.actions.append({'release_lock': True, 'accepted':  True})
        return self.actions