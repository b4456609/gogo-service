import collections

SunTime = collections.namedtuple('SunTime',
                                 ['sunrise', 'sunset'])
BasicMetrics = collections.namedtuple('BasicMetrics',
                                      ['time', 'temp', 'humd', 'wind_speed_10min', 'wind_dir_10min'])
RainDetail = collections.namedtuple('RainDetail',
                                    ['time', 'rain_10min', 'rain_60min', 'rain_3hr', 'rain_6hr', 'rain_12hr',
                                     'rain_24hr'])
AirPollution = collections.namedtuple('AirPollution', ['psi', 'pm2_5'])

class Metrics():
    def __init__(self, SunTime, BasicMetrics, RainDetail, AirPollution):
        self.SunTime = SunTime;
        self.BasicMetrics = BasicMetrics;
        self.RainDetail = RainDetail;
        self.AirPollution = AirPollution;