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
from davan.http.service.base_service import BaseService
import davan.util.helper_functions as helper


class WaterLevelMonitorService(BaseService):
    '''
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,constants.WATER_LEVEL_MONITOR_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.level = 0
        self.status = "Sleeping"
        
    def handle_request(self, msg):
        try:
            self.logger.info("Received request: " + str(msg))

            if msg.endswith("Wakeup"):
                self.status = "Working"
            elif msg.endswith("GoToSleep"):
                self.status = "Sleeping"
            else:
                self.level = msg.replace("/WaterLevelMonitorService?distance=", "")
                self.update_virtual_device();
        except Exception as ex:
           self.logger.info("Caught exception " + str(ex))
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")
                                             
    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def update_virtual_device(self):
        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_PUMP_ID'],
                                self.config['FIBARO_VD_PUMP_MAP']['distance'],
                                str(self.level))
        #self.logger.info("Url: "+ url)
        helper.send_auth_request(url,self.config)

    def get_html_gui(self, column_id):
        """
        Override and provide gui
        """
        if not self.is_enabled():
            return BaseService.get_html_gui(self, column_id)

        result = "\nLevel: " + str(self.level) + "</br>\n"
        result += "Status: " + str(self.status) + "</br>\n"

        result +="MinLimit: " + str(self.config['WaterLevelMinLimit']) + "</br>\n" 
        result +="MaxLimit: " + str(self.config['WaterLevelMaxLimit']) + "</br>\n" 
         
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", result)
        return column
        
if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = WaterLevelMonitorService(None, config)
