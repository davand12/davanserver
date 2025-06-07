#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
@author: davandev
'''
import logging
import os
import json
import urllib
import traceback

import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper
from davan.util import application_logger as log_manager
from davan.http.service.reoccuring_base_service import ReoccuringBaseService
import davan.util.helper_functions as helper


class MoistureMonitorService(ReoccuringBaseService):
    '''
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self,constants.MOISTURE_MONITOR_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.humidity_value = 0
                
        
    def get_next_timeout(self):
        return self.config['MoistureMonitorTimeout']
                                             
    def handle_timeout(self):
        '''
        Timeout received, iterate all active scenes to check that they are running on fibaro 
        system, otherwise start them
        '''
        try:
            self.fetch_moisture_value()
            self.logger.debug("Humidity:"+str(self.humidity_value))
            self.maybe_notify_value()

        except Exception:
            self.logger.error(traceback.format_exc())
            self.increment_errors()

    def maybe_notify_value(self):
        if self.humidity_value >= self.config['MoistureMaxLimit']:
            self.logger.info("Humidity value higher exceeds limit, send notifications")
            helper.send_telegram_message(self.config, "Luftfuktigheten i badrummet["+str(self.humidity_value)+"], var god och ventilera")
            msg = "Det är "+str(self.humidity_value)+" procents luftfuktighet i badrummet, sätt på fläkten"
            self.services.get_service(constants.TTS_SERVICE_NAME).start(msg,constants.SPEAKER_KITCHEN)
                        
    def fetch_moisture_value(self):
        '''
        Fetch and parse alarm status
        '''
        result = helper.send_auth_request(
            self.config['FIBARO_API_ADDRESS'] +"devices?id=" + self.config['MoistureVdId'],
            self.config)

        res = result.read()
        data = json.loads(res)

        moistureLevel = data['properties']
        self.humidity_value = int(float(moistureLevel['value'])) 

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

        result = "Bathroom humidity: " + str(self.humidity_value) + "</br>\n"
        result +="MaxLimit: " + str(self.config['MoistureMaxLimit']) + "</br>\n" 
         
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", result)
        return column
        
if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = MoistureMonitorService(None, config)
    test.fetch_moisture_value()
    test.maybe_notify_value()