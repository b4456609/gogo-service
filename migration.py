from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.usertype import UserType
from cassandra.cqlengine import management

import model
import model1


connection.setup(['140.121.101.164'], "weather1")

location = 'Jhongjheng District, Keelung City'
q = model.Weather.objects()
array = []
for i in q:
    print i
    w1 = model1.Weather(location= location, time=i.time, uv=i.uv, air=i.air, sun=i.sun, rain=i.rain, basic=i.basic, value=i.value, predict=i.predict)
    array.append(w1)
    
    
    
connection.setup(['140.121.101.164'], "weather2")
for i in array:
    i.save()