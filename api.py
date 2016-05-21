from flask import Flask
from flask import jsonify
from flask import request
import datetime
import json
import model
from  dateutil.parser import parse
from cassandra.cqlengine import connection
from flask.ext.cors import CORS
import pytz
from cassandra.cluster import Cluster

app = Flask(__name__)
CORS(app)


def addItem(q, temp, humid, rain, time):
    for i in q:
        # j = {
        #     "air": {
        #         "psi": i.air.psi,
        #         "pm2_5": i.air.pm2_5
        #     },
        #     "sun": {
        #         "sunset": datetime.time(i.sun.sunset.hour, i.sun.sunset.minute, i.sun.sunset.second).isoformat(),
        #         "sunrise": datetime.time(i.sun.sunrise.hour, i.sun.sunrise.minute, i.sun.sunrise.second).isoformat()
        #     },
        #     "uv": i.uv,
        #     "rain": {
        #         "rain_10min": i.rain.rain_10min,
        #         "rain_60min": i.rain.rain_60min,
        #         "rain_3hr": i.rain.rain_3hr,
        #         "rain_6hr": i.rain.rain_6hr,
        #         "rain_12hr": i.rain.rain_12hr,
        #         "rain_24hr": i.rain.rain_24hr
        #     },
        #     "basic": {
        #         "wind_dir_10min": i.basic.wind_dir_10min,
        #         "wind_speed_10min": i.basic.wind_speed_10min,
        #         "humd": i.basic.humd,
        #         "temp": i.basic.temp,
        #     },
        #     "time": pytz.timezone('Asia/Taipei').localize(i.time).isoformat()
        # }
        # if i.value is not None:
        #     value = {
        #         "sun": i.value.sun,
        #         "weather": i.value.weather,
        #         "uv": i.value.uv,
        #         "rain": i.value.rain,
        #         "air": i.value.air
        #     }
        #     j['value'] = value

        temp.append(round(i.basic.temp, 2))
        humid.append(round(i.basic.humd * 100, 2))
        time.append(pytz.timezone('Asia/Taipei').localize(i.time + datetime.timedelta(hours=8)).isoformat())
        rain.append(max(i.rain.rain_10min, 0))


def getWindAnalysis(q):
    res = []

    for i in range(36):
        res.append({
            "d": i * 10,
            "count": 0,
            "avg": 0
        })

    res.append({
        "d": None,
        "count": 0,
        "avg": 0
    })

    for i in q:
        if i.basic.wind_dir_10min >= 0:
            res[i.basic.wind_dir_10min / 10]['count'] += 1
            res[i.basic.wind_dir_10min / 10]['avg'] += i.basic.wind_speed_10min
        else:
            res[36]['count'] += 1

    for i in res:
        if i['count'] is not 0:
            i['avg'] /= i['count']

    return res


@app.route('/', methods=['GET'])
def getWeather():
    temp = []
    humid = []
    time = []
    rain = []
    radarData = {}
    metric = {}

    q = model.Weather.objects(date=datetime.date.today().isoformat()).limit(36).order_by('-time')
    # q = model.Weather.objects()

    addItem(q, temp, humid, rain, time)
    if q.count() < 36:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        q = model.Weather.objects(date=yesterday.isoformat()).limit(36 - q.count()).order_by('-time')
        addItem(q, temp, humid, rain, time)

    if q.count() > 0:
        radarData = {
            "sun": q[0].value.sun,
            "weather": q[0].value.weather,
            "uv": q[0].value.uv,
            "rain": q[0].value.rain,
            "air": q[0].value.air,
            "predict": q[0].value.predict
        }
        metric = {
            'temp': round(q[0].basic.temp, 2),
            'humd': round(q[0].basic.humd * 100, 2),
            'uv': q[0].uv,
            'pm2_5': q[0].air.pm2_5,
            'psi': q[0].air.psi,
            'sunset': datetime.time(q[0].sun.sunset.hour, q[0].sun.sunset.minute,
                                    q[0].sun.sunset.second).isoformat(),
            'sunrise': datetime.time(q[0].sun.sunset.hour, q[0].sun.sunset.minute,
                                     q[0].sun.sunset.second).isoformat(),
            'wind': max(round(q[0].basic.wind_speed_10min, 2), 0),
        }

    # ::-1 reverse list
    resp = {
        'tempHumidRainChart': {
            'temp': temp,
            'humid': humid[::-1],
            'rain': rain[::-1],
            'time': time[::-1]
        },
        'radar': radarData,
        'metric': metric,
        'windChart': getWindAnalysis(q)
    }
    print resp
    return json.dumps(resp), 200, {'Content-Type': 'application/json'}


@app.route('/', methods=['POST'])
def addWeather():
    app.logger.debug(request.data)
    j = request.get_json()
    app.logger.debug(j)

    air = model.Air(psi=j['air']['psi'], pm2_5=j['air']['pm2_5'])
    app.logger.debug(air)

    sun = model.Sun(sunset=parse(j['sun']['sunset']).time(), sunrise=parse(j['sun']['sunrise']).time())
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

    value = model.Value(
        sun=j['value']['sun'],
        weather=j['value']['weather'],
        uv=j['value']['uv'],
        rain=j['value']['rain'],
        air=j['value']['air'],
        predict=j['value']['predict'],
    )

    weather = model.Weather(
        date=parse(j['basic']['time']),
        time=parse(j['basic']['time']),
        uv=j['uv'],
        air=air,
        sun=sun,
        rain=rain,
        basic=basic,
        value=value,
        predict=model.trasformPredictMetrics(j['predictMetrics'])
    )

    app.logger.debug(j['predictMetrics'])
    app.logger.debug(weather)

    weather.save()

    return json.dumps({'success': True}), 200, {'Content-Type': 'application/json'}


@app.route('/multi', methods=['POST'])
def addMultiWeather():
    app.logger.debug(request.data)
    d = request.get_json()
    app.logger.debug(d)

    for j in d:
        air = model.Air(psi=j['air']['psi'], pm2_5=j['air']['pm2_5'])
        app.logger.debug(air)

        sun = model.Sun(sunset=parse(j['sun']['sunset']).time(), sunrise=parse(j['sun']['sunrise']).time())
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

        value = None
        if 'value' in j:
            value = model.Value(
                sun=j['value']['sun'],
                weather=j['value']['weather'],
                uv=j['value']['uv'],
                rain=j['value']['rain'],
                air=j['value']['air']
            )

        weather = model.Weather(
            date=parse(j['time']),
            time=parse(j['time']),
            uv=j['uv'],
            air=air,
            sun=sun,
            rain=rain,
            basic=basic,
            value=value,
            predict=j['predictMetrics']
        )
        app.logger.debug(j['predictMetrics'])
        app.logger.debug(weather)

        weather.save()

    return json.dumps({'success': True}), 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    # connect to test keyspace
    connection.setup(['140.121.101.164'], "weather1")
    app.run(debug=True, host='0.0.0.0')
