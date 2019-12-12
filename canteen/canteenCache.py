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
		
	def showCache(self):
		return self.db

	def checkCache(self,day):
		"""
		Check if there is a menu of the argument day on the cache 
		"""	
		if self.db == {}:	
			print("Não existe na Cache")
			return False
		try:
			if day in self.db['info'].keys():
				print("Existe na Cache")
				return True
		except:
			print("Não existe na Cache")
			return False

	def transform(self,day=None,type = None):
		"""
		Retrieve the information from the cache
		"""
		new = {}
		new["name"] = "Canteen"
		new["info"] = {}
		for i in self.db["info"]:
			if i == day or day == None:
				new["info"][i] = {}
				for j in self.db['info'][i]:
					if j == type.capitalize() or type == None:
						new["info"][i][j] = self.db["info"][i][j]

		return new
