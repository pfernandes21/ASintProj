import uuid
import pickle

class Service:
    def __init__(self,Location,Name,Description,OpeningHours):
        self.Location = Location
        self.Name = Name
        self.Description = Description
        self.OpeningHours = OpeningHours
        self.id = str(uuid.uuid1())

class DBService:
    def __init__(self, name):
        self.name = name
        try:
                f = open('serviceDB'+self.name, 'rb')
                self.db = pickle.load(f)
                f.close()
        except IOError:
                self.db = {}

    def addService(self,location,name,description,opening):
        service = Service(location,name,description,opening)
        self.db[service.id] = service
        f = open('serviceDB'+self.name, 'wb')
        pickle.dump(self.db, f)
        f.close()

        print(self.db)
        print("elemento inserido")
        print(self.db[service.id])
        print(service.id)

    def rmService(self,id):
        del self.db[id]
        f = open('serviceDB'+self.name, 'wb')
        pickle.dump(self.db, f)
        f.close()

    def listAllServices(self):
        services = {}
        flag = True

        for key in self.db:
            services[self.db[key].Name] = key
            flag = False
        
        if flag:
            return None

        return services

    def showService(self,id):
        print(id)
        print(self.db[str(id)])
        return self.db[id]