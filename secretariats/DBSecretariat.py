import uuid
import pickle

class Secretariat:
    """
    Class that represent one Secretariat
    """
    def __init__(self,Location,Name,Description,OpenTime):
        self.Name = Name
        self.Location = Location
        self.Description = Description
        self.OpenTime = OpenTime
        self.id = str(uuid.uuid1())

class DBSecretariat:
    """
    DataBase that saves all the Secretariats
    """
    def __init__(self, name):
        self.name = name
        try:
                f = open('secretariatDB'+self.name, 'rb')
                self.db = pickle.load(f)
                f.close()
        except IOError:
                self.db = {}

    def addSecretariat(self,location,name,description,opening):
        secretariat = Secretariat(location,name,description,opening)
        self.db[secretariat.id] = secretariat
        f = open('secretariatDB'+self.name, 'wb')
        pickle.dump(self.db, f)
        f.close()

    def rmSecretariat(self,id):
        del self.db[id]
        f = open('secretariatDB'+self.name, 'wb')
        pickle.dump(self.db, f)
        f.close()

    def changeSecretariat(self,id,key,value):
        try:
            secretariat = self.db[id]
        except:
            return "Wrong ID"
        try:
            if key.lower() == "location": 
                secretariat.Location = value
            elif key.lower() == "name": 
                secretariat.Name = value
            elif key.lower() == "description": 
                secretariat.Description = value
            elif key.lower() == "opentime": 
                secretariat.OpenTime = value
        except:
            return "Wrong Json"
        f = open('secretariatDB'+self.name, 'wb')
        pickle.dump(self.db, f)
        f.close()
        return "Success"

    def listAllSecretariats(self):
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

    def showSecretariat(self,id):
        """
        Return the secretariat that has an id equals to the argument id
        """
        print(id)
        print(self.db[str(id)])
        return self.db[id]