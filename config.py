class Canteen:
   def  __init__(self):
       self.host = '127.0.0.1'
       self.port = 8000

class Rooms:
   def  __init__(self):
       self.host = '127.0.0.1'
       self.port = 6000

class Secretariats:
   def  __init__(self):
       self.host = '127.0.0.1'
       self.port = 7000

class Backend:
   def  __init__(self):
       self.host = '127.0.0.1'
       self.port = 5000

class Log:
   def  __init__(self):
       self.host = '127.0.0.1'
       self.port = 5002
    
def dictMicroservices():
    dicio = {}
    dicio['canteen'] = "http://%s:%d"%(Canteen().host,Canteen().port)
    dicio['Log'] = "http://%s:%d"%(Log().host,Log().port)
    dicio['secretariats'] = "http://%s:%d"%(Secretariats().host,Secretariats().port)
    dicio['rooms'] = "http://%s:%d"%(Rooms().host,Rooms().port)
    return dicio