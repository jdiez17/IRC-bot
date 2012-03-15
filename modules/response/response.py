class Response():
	def __init__(self):
		self.actions = [{'acquire_lock': True}]
	
	def add_action(self, action):
		self.actions.append(action)
	
	def generate_response(self):
		self.acctions.append({'release_lock': True})
		return self.actions