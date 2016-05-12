from flask import Flask
from flask import jsonify
from flask import request
import json

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
    app.logger.debug(request.get_json())
    json = request.get_json()
    app.logger.debug(json['username'])
    return json['username']


if __name__ == '__main__':
    app.run(debug=True)
