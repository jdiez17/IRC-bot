class Response():
	def __init__(self):
		self.actions = []
	
	def add_action(self, action):
		self.actions.append(action)
	
	def generate_response(self):
		return self.actions