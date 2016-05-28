from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.usertype import UserType
from cassandra.cqlengine import management
import api


class Air(UserType):
    psi = columns.Integer()
    pm2_5 = columns.Integer()


class Sun(UserType):
    sunset = columns.Time()
    sunrise = columns.Time()


class Rain(UserType):
    rain_10min = columns.Float()
    rain_60min = columns.Float()
    rain_3hr = columns.Float()
    rain_6hr = columns.Float()
    rain_12hr = columns.Float()
    rain_24hr = columns.Float()

class Basic(UserType):
    wind_dir_10min = columns.Integer()
    wind_speed_10min = columns.Float()
    humd = columns.Float()
    temp = columns.Float()


class Value(UserType):
    sun = columns.Integer()
    weather = columns.Integer()
    uv = columns.Integer()
    rain = columns.Integer()
    air = columns.Integer()
    predict = columns.Integer()

class Weather(Model):
    location = columns.Text(primary_key=True)
    time = columns.DateTime(primary_key=True)
    uv = columns.Float()
    air = columns.UserDefinedType(Air)
    sun = columns.UserDefinedType(Sun)
    rain = columns.UserDefinedType(Rain)
    basic = columns.UserDefinedType(Basic)
    value = columns.UserDefinedType(Value)
    predict = columns.Map(columns.Text, columns.List(columns.Text))


# transform int to str for db need
def trasformPredictMetrics(data):
    res = {}
    if data is not None:
        res['humid'] = map(lambda x: str(x), data['humid'])
        res['predictRate'] = map(lambda x: str(x), data['predictRate'])
        res['temp'] = map(lambda x: str(x), data['temp'])
        res['predictTime'] = data['predictTime']
        res['time'] = data['time']
    return res


# transform int to str for db need
def trasformPredictMetricsToInt(data):
    res = {}
    if 'predictTime' in data:
        res['predictTime'] = data['predictTime']
        res['time'] = data['time']
        res['humid'] = []
        res['predictRate'] = []
        res['temp'] = []
        for i in data['humid']:
            res['humid'].append(int(i))

        for i in data['predictRate']:
            res['predictRate'].append(int(i))

        for i in data['temp']:
            res['temp'].append(int(i))
    return res

def main():
    # create a keyspace "test"
    connection.setup(['140.121.101.164'], "weather1")
    management.create_keyspace_simple('weather2', 3)

    # connect to test keyspace
    connection.setup(['140.121.101.164'], "weather2")

    management.sync_type('test', Air)
    management.sync_type('test', Sun)
    management.sync_type('test', Rain)
    management.sync_type('test', Basic)
    management.sync_type('test', Value)
    management.sync_table(Weather)

# main()
