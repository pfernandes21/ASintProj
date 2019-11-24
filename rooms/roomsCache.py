import pickle


class Cache:
	def __init__(self, name):
		self.name = name
		try:
			f = open('roomsDB'+self.name, 'rb')
			self.db = pickle.load(f)
			f.close()
		except IOError:
			self.db = {}

	def add(self, id, cache):
		self.db[str(id)] = cache
		f = open('roomsDB'+self.name, 'wb')
		pickle.dump(self.db, f)
		f.close()

	def change(self):
		pass
		
	def showCache(self, id):
		return self.db[str(id)]

	def checkCache(self,id):
		if self.db == {}:	
			print("Não existe na Cache")
			return False
		if str(id) in self.db.keys():
			print("Existe na Cache")
			return True
		else:
			print("Não existe na Cache")
			return False