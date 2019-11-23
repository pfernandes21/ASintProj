import pickle


class Cache:
	def __init__(self, name):
		self.name = name
		try:
			f = open('CanteenDB'+self.name, 'rb')
			self.db = pickle.load(f)
			f.close()
		except IOError:
			self.db = {}

	def add(self,cache):
		self.db = cache
		f = open('CanteenDB'+self.name, 'wb')
		pickle.dump(self.db, f)
		f.close()

	def change(self):
		pass
		
	def showCache(self):
		return self.db

	def checkCache(self,day):
		if self.db == {}:	
			print("Não existe na Cache")
			return False
		if day in self.db['type'].keys():
			print("Existe na Cache")
			return True
		else:
			print("Não existe na Cache")
			return False