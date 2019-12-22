import pickle
from datetime import datetime, timedelta
import os

class Cache:
	def __init__(self, name):
		self.name = name
		try:
			f = open('roomsDB'+self.name, 'rb')
			self.db = pickle.load(f)
			f.close()
		except IOError:
			self.db = {}
			self.db["updatedAt"] = datetime.now()

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
		"""
		Check if there is a room or building with the id
		"""	
		if self.db == {}:	
			print("Não existe na Cache")
			return False
		#if 24 hours passed since the cache was updated, the cache is reset
		if (datetime.now() - self.db["updatedAt"]).total_seconds()/3600 > 24:
			print("Cache desatualizada")
			if os.path.exists("roomsDB"):
  				os.remove("roomsDB")
			self.db["updatedAt"] = datetime.now()
			return False
		if str(id) in self.db.keys():
			print("Existe na Cache")
			return True
		else:
			print("Não existe na Cache")
			return False