from flask import Flask
from flask import jsonify
from flask import request
import datetime
import json
import model

app = Flask(__name__)


class Weather(object):
    def __init__(self, humid, temp):
        self.humidd = humid
        self.temp = temp


w = Weather(1, 2)


@app.route('/', methods=['GET'])
def index():
    return jsonify(w.__dict__)


@app.route('/', methods=['POST'])
def hello():
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

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(debug=True)
