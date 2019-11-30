import uuid
import pickle

class Service:
    def __init__(self,Location,Name,Description,OpenTime):
        self.Location = Location
        self.Name = Name
        self.Description = Description
        self.OpenTime = OpenTime
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

    def rmService(self,id):
        del self.db[id]
        f = open('serviceDB'+self.name, 'wb')
        pickle.dump(self.db, f)
        f.close()

    def changeService(self,id,key,value):
        try:
            service = self.db[id]
        except:
            return "Wrong ID"
        try:
            if key.lower() == "location": 
                service.Location = value
            elif key.lower() == "name": 
                service.Name = value
            elif key.lower() == "description": 
                service.Description = value
            elif key.lower() == "opentime": 
                service.OpenTime = value
        except:
            return "Wrong Json"
        f = open('serviceDB'+self.name, 'wb')
        pickle.dump(self.db, f)
        f.close()
        return "Success"

    def listAllServices(self):
        services = {}
        flag = True

        for key in self.db:
            services[self.db[key].Location] = {}
            

        for key in self.db:
            services[self.db[key].Location][self.db[key].Name]= key
            flag = False
        
        if flag:
            return None

        return services

    def showService(self,id):
        print(id)
        print(self.db[str(id)])
        return self.db[id]