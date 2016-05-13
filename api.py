from flask import Flask
from flask import jsonify
from flask import request
import datetime
import json
import model
from cassandra.cqlengine import connection

app = Flask(__name__)


@app.route('/', methods=['GET'])
def getWeather():
    res = []
    q = model.Weather.objects()
    for i in q:
        j = {
            "air": {
                "psi": i.air.psi,
                "pm2_5": i.air.pm2_5
            },
            "sun": {
                "sunset": datetime.time(i.sun.sunset.hour,i.sun.sunset.minute,i.sun.sunset.second).isoformat(),
                "sunrise": datetime.time(i.sun.sunrise.hour,i.sun.sunrise.minute,i.sun.sunrise.second).isoformat()
            },
            "uv": i.uv,
            "rain": {
                "rain_10min": i.rain.rain_10min,
                "rain_60min": i.rain.rain_60min,
                "rain_3hr": i.rain.rain_3hr,
                "rain_6hr": i.rain.rain_6hr,
                "rain_12hr": i.rain.rain_12hr,
                "rain_24hr": i.rain.rain_24hr
            },
            "basic": {
                "wind_dir_10min": i.basic.wind_dir_10min,
                "wind_speed_10min": i.basic.wind_speed_10min,
                "humd": i.basic.humd,
                "temp": i.basic.temp,
                "time": i.basic.time
            }
        }
        res.append(j)
    print res
    return json.dumps(res), 200, {'Content-Type': 'application/json'}


@app.route('/', methods=['POST'])
def addWeather():
    app.logger.debug(request.data)
    j = request.get_json()
    app.logger.debug(j)

    air = model.Air(psi=j['air']['psi'], pm2_5=j['air']['pm2_5'])
    app.logger.debug(air)

    sun = model.Sun(sunset=j['sun']['sunset'], sunrise=j['sun']['sunset'])
    app.logger.debug(sun)

    rain = model.Rain(
        rain_10min=j['rain']['rain_10min'],
        rain_60min=j['rain']['rain_60min'],
        rain_3hr=j['rain']['rain_3hr'],
        rain_6hr=j['rain']['rain_6hr'],
        rain_12hr=j['rain']['rain_12hr'],
        rain_24hr=j['rain']['rain_24hr']
    )
    app.logger.debug(rain)

    basic = model.Basic(
        wind_dir_10min=j['basic']['wind_dir_10min'],
        wind_speed_10min=j['basic']['wind_speed_10min'],
        humd=j['basic']['humd'],
        temp=j['basic']['temp']
    )
    app.logger.debug(basic)

    weather = model.Weather(
        time=datetime.datetime.strptime(j['basic']['time'], "%Y-%m-%dT%H:%M:%S"),
        uv=j['uv'],
        air=air,
        sun=sun,
        rain=rain,
        basic=basic
    )
    app.logger.debug(weather)

    weather.save()

    return json.dumps({'success': True}), 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    # connect to test keyspace
    connection.setup(['140.121.101.164'], "test")
    app.run(debug=True)
