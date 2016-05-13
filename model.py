from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.usertype import UserType
from cassandra.cqlengine import management


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

class Weather(Model):
    time = columns.DateTime(primary_key=True)
    uv = columns.Float()
    air = columns.UserDefinedType(Air)
    sun = columns.UserDefinedType(Sun)
    rain = columns.UserDefinedType(Rain)
    basic = columns.UserDefinedType(Basic)

def main():
    # create a keyspace "test"
    connection.setup(['140.121.101.164'], "test")
    management.create_keyspace_simple('test', 3)

    # connect to test keyspace
    connection.setup(['140.121.101.164'], "test", protocol_version=3)

    management.sync_type('test', Air)
    management.sync_type('test', Sun)
    management.sync_type('test', Rain)
    management.sync_type('test', Basic)
    management.sync_table(Weather)

main()