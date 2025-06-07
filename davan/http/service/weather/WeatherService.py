# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import logging
import os
import json
import urllib.request, urllib.error, urllib.parse
import urllib.request, urllib.parse, urllib.error
import traceback

import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper

from davan.http.service.reoccuring_base_service import ReoccuringBaseService


class WeatherService(ReoccuringBaseService):
    '''
    classdocs
    Example urls
    current condition: https://api.weather.com/v2/pws/observations/current?stationId=&format=json&units=m&apiKey=
    forecast: https://api.weather.com/v3/wx/forecast/daily/5day?geocode=&format=json&units=s&language=sv-SE&apiKey=
    '''
    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.WEATHER_SERVICE, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))

        self.is_raining = False
        self.time_to_next_timeout = 180
        self.forecast  =""
        self.temp = -1
        self.rain = 0
        self.pressure = 0
        self.wunderground_url =""
        self.forecast_url =""
        self.virtualdevice_id="79"

        self.weather_data = {
                                "Temp":{'DataTag':'temp','Value':"0",'LabelId':'ui.lblTemp.value'},
                                "Rain":{'DataTag':'precipRate','Value':"0",'LabelId':'ui.lblRain.value'},
                                "Pressure":{'DataTag':'pressure','Value':"0",'LabelId':'ui.lblPressure.value'},
                                "Humidity":{'DataTag':'humidity','Value':"0",'LabelId':'ui.lblHumidity.value'},
                                "Time":{'DataTag':'obsTimeLocal','Value':"0",'LabelId':'ui.lblTime.value'}
                            }
    def init_service(self):
        self.wunderground_url = self.config["WEATHER_API_PATH"].replace("<API_KEY>",self.config["WEATHER_TOKEN"])
        self.wunderground_url = self.wunderground_url.replace("<STATIONID>",self.config["WEATHER_STATION_ID"])
        self.forecast_url = self.config["WEATHER_FORECAST_PATH"].replace("<API_KEY>",self.config["WEATHER_TOKEN"])
        self.forecast_url = self.forecast_url.replace('<GEO_CODE>',self.config["WEATHER_GEOCODE"])

    def do_self_test(self):
        try:
            self.logger.info("Perform self test")
            #self._fetch_current_conditions()
            self._fetch_forecast()

            #self.check_rain()
            #self.update_virtual_device()
        except:
            self.logger.error(traceback.format_exc())

            self.logger.warning("Self test failed")
            msg = "Failed to fetch weather"
            self.raise_alarm(msg,"Warning",msg)

    def _fetch_current_conditions(self):
        result = (urllib.request.urlopen(self.wunderground_url))
        raw_data = result.read()
        encoding = result.info().get_content_charset('utf8')  # JSON default

        self.result_data = json.loads(raw_data.decode(encoding))            
        
        observations = self.result_data["observations"][0]
        for measure_type in self.weather_data.values():
            if measure_type['DataTag'] in observations.keys():
                value = observations[measure_type['DataTag']]
                measure_type['Value'] = value

        metric = observations["metric"]
        for measure_type in self.weather_data.values():
            if measure_type['DataTag'] in metric.keys():
                value = metric[measure_type['DataTag']]
                measure_type['Value'] = value

    def handle_request(self, msg):
        '''
        Handle received http request 
        @return latest received weather data
        '''
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, "" 
    
    def handle_timeout(self):
        '''
        Timeout received, fetch weather data from wunderground
        '''
        self.logger.debug("Fetch weather")
        try:
            #self._fetch_current_conditions()
            self._fetch_forecast()
            #self.check_rain()
            #0self.update_virtual_device()
        except Exception:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            pass
    
    def get_next_timeout(self):
        '''
        Return time in seconds to next timeout
        '''
        return self.time_to_next_timeout
    
    def update_virtual_device(self):
        '''
        Update weather virtual device on HC2 
        '''
        for measure_type in self.weather_data.values():
            url = helper.createFibaroUrl(
                self.config['UPDATE_DEVICE'], 
                self.virtualdevice_id, 
                measure_type['LabelId'], 
                str(measure_type['Value']))      
            self.logger.debug("URL:"+url)
            helper.send_auth_request(url,self.config)                  

                
    def check_rain(self):
        '''
        Check if it is raining, then notify on telegram
        '''

        rain_data = self.weather_data['Rain']
        self.logger.debug("Check if it is raining["+str(rain_data['Value'])+"]")
        if not (str(rain_data['Value']) == "0.0" or str(rain_data['Value']) == "0"):
            if not self.is_raining:
                self.logger.info("It has started to rain")
                helper.send_telegram_message(self.config, constants.RAIN_STARTED)
                self.services.get_service(constants.TTS_SERVICE_NAME).start(
                    constants.RAIN_STARTED,
                    constants.SPEAKER_KITCHEN)
                self.is_raining = True

        else:
            if self.is_raining:
                self.logger.info("It has stopped to rain")
                helper.send_telegram_message(self.config, constants.RAIN_STOPPED)
                self.services.get_service(constants.TTS_SERVICE_NAME).start(
                    constants.RAIN_STOPPED,
                    constants.SPEAKER_KITCHEN)
                self.is_raining = False
    
    def _fetch_forecast(self): 
        '''
        Fetch the forecast 
        '''
        result = (urllib.request.urlopen(self.forecast_url))
        raw_data = result.read()
        encoding = result.info().get_content_charset('utf8')  # JSON default
        forecast = json.loads(raw_data.decode(encoding))   
        forecastToday=forecast['daypart'][0]['narrative'][0]         
        forecastToNight=forecast['daypart'][0]['narrative'][1]         
        forecastTomorrow=forecast['daypart'][0]['narrative'][2]         
        self.forecast=forecastToday
        
        self.logger.debug(forecastToday)
                
                
    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, column_id):
        """
        Override and provide gui
        """
        if not self.is_enabled():
            return ReoccuringBaseService.get_html_gui(self, column_id)

        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        if self.weather_data == None:
            htmlresult = "<li>No weather data available</li>\n"            
        else:
            htmlresult = "<li>Temp: " + str(self.weather_data['Temp']['Value']) + "</li>\n"
            htmlresult += "<li>Humidity: " + str(self.weather_data['Humidity']['Value']) + " </li>\n"
            htmlresult += "<li>Pressure: " + str(self.weather_data['Pressure']['Value']) + " bar </li>\n"
            htmlresult += "<li>Rain: " + str(self.weather_data['Rain']['Value']) + " mm</li>\n"
            htmlresult += "<li>Time: " + str(self.weather_data['Time']['Value']) + " </li>\n"
            htmlresult += "Forecast: " + str(self.forecast)
        column = column.replace("<SERVICE_VALUE>", htmlresult)
        return column

    def get_announcement(self):
        '''
        Compose and encode announcement data
        '''
        
        self.logger.info("Create weather announcement")
        if self.weather_data == None:
            self.logger.warning("Cached service data is none")
            return ""
        try:
#        temp = str(self.weather_data['Temp']['Value'])
#        temp = temp.replace(".",",")
#        announcement = "Just nu är det "
#        announcement += temp + " grader ute. "

           self.forecast = self.forecast.replace('ºC', ' grader')
           self.forecast = self.forecast.replace('°', ' grader')
           self.logger.info("Dagens prognos: "+ self.forecast)
           announcement = "Dagens väderprognos." +self.forecast+". "
           return announcement
        except Exception:
            return ""
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = WeatherService()
    test.handle_request("msg")
