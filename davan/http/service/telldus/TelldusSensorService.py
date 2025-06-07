'''
@author: davandev
'''
import logging
import os
from urllib.parse import quote
import urllib.request, urllib.parse, urllib.error
import datetime
import traceback
from threading import Thread,Event

import davan.http.service.telldus.tdtool as telldus
import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper
from davan.http.service.reoccuring_base_service import ReoccuringBaseService


class TelldusSensorService(ReoccuringBaseService):
    '''
    Starts a re-occuring service that fetches sensor values from Telldus Live and 
    pushes the results(temperature, humidity and date) of each sensor to a 
    virtual device on the Fibaro system. 
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.TELLDUS_SENSOR_SERVICE, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.time_to_next_timeout = 900

    def get_next_timeout(self):
        return self.time_to_next_timeout    
                                         
    def handle_timeout(self):
        '''
        Timeout received, fetch sensor values from Telldus Live
        Push sensor data to Fibaro virtual device  
        '''
        self.logger.debug("Fetch telldus sensor values")

        response=telldus.listSensorsAndValues()
        if not 'sensor' in str(response):
            self.logger.error("No response received from telldus")
            self.logger.debug("Received response [" + str(response) + "]")
            helper.send_telegram_message(self.config, "Telldus svarar inte") 
            return 
        for sensor in response['sensor']:
            name = "%s" % (sensor['name'])
            
            if name in self.config["SENSOR_MAP"]:
                sensorUrl = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                                   self.config["SENSOR_MAP"][name], 
                                                   self.config['LABEL_TEMP'], 
                                                   sensor['temp'])

                self.sendUrl(sensorUrl)
                sensorUrl = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                                   self.config["SENSOR_MAP"][name], 
                                                   self.config['LABEL_DATE'], 
                                                   str(datetime.datetime.fromtimestamp(int(sensor['lastUpdated']))))
                self.sendUrl(sensorUrl)
                if 'humidity' in sensor:
                    sensorUrl = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                                       self.config["SENSOR_MAP"][name], 
                                                       self.config['LABEL_HUMIDITY'], 
                                                       sensor['humidity'])
                    self.sendUrl(sensorUrl)
                    self.maybe_notify_humidity_level(sensor['name'], sensor['humidity'])
                          
        
    def sendUrl(self, url):
        '''
        Update fibaro system with sensor values
        @param url, url with sensor values
        '''
        urllib.request.urlopen(url)        

    def maybe_notify_humidity_level(self, sensor_name, humidity_value):
        '''
        Check if the received humidity value is higher than the configured limit.
        If higher then send telegram notifications to all configured receivers.
        @param sensor_name, name of the sensor
        @param humidity_value, humidity value
        '''
        try:
            if sensor_name in self.config["SENSOR_HUMIDITY_LIMITS"]:
#                self.logger.info("Sensor "+ sensor_name +" has humidity limits configured. Current value["+humidity_value+"]")
                
                sensor_limit = self.config['SENSOR_HUMIDITY_LIMITS'][sensor_name]
                if int(humidity_value) > sensor_limit :
                    self.logger.info("Humidity value higher exceeds limit, send notifications")
                    helper.send_telegram_message(self.config, "Luftfuktigheten i badrummet["+humidity_value+"], var god och ventilera")
                    msg = "Det är "+str(humidity_value)+" procents luftfuktighet i badrummet, sätt på fläkten"
                    self.services.get_service(constants.TTS_SERVICE_NAME).start(msg,constants.SPEAKER_KITCHEN)
        except :
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=3)
    
    test = TelldusSensorService()
