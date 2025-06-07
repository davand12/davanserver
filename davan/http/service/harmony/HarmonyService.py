# -*- coding: utf-8 -*-

'''
@author: davandev
'''
import logging
import os
import json
import urllib.request, urllib.parse, urllib.error

import davan.util.cmd_executor as executor
import davan.util.constants as constants
import davan.util.helper_functions as helper_functions
from davan.http.service.base_service import BaseService

class HarmonyService(BaseService):
    '''
    This service requires HA-bridge or hue-bridge as proxy to forward button presses on the remote control.
    Download from https://github.com/bwssytems/ha-bridge/blob/master/README.md
    Each button is configured in the harmony app to forward requests to HarmonyService 
    http device, TvLightsOn, http://192.168.50.43:8080/HarmonyService?TvLightOn, http Get
    http device, TvLightsOff, http://192.168.50.43:8080/HarmonyService?TvLightOff, http Get
    http device, PowerOff, http://192.168.50.43:8080/HarmonyService?PowerOff, http Get
    http device, PowerOn, http://192.168.50.43:8080/HarmonyService?PowerOn, http Get
    start service : java -jar ha-bridge-5.4.1.jar
    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.HARMONY_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))

    def parse_request(self, msg):
        res = msg.split('?')
        return res[1]

    def handle_request(self, msg):
        action = self.parse_request(msg)

        self.logger.info("Received request ["+action+"]")
        self.perform_action(action)
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")

    def perform_action(self, action) :
        tuya = self.services.get_service(constants.TUYA_SERVICE_NAME)
        tradfri = self.services.get_service(constants.TRADFRI_SERVICE_NAME)

        if( action == "TvLightOn"):
            self.logger.info("TurnOnTvLight")
            tuya.handle_request("?Upstairs_Light=On" )
            tradfri.handle_request("?TvRoomGroup=on" )

        elif( action == "TvLightOff"):         
            self.logger.info("TurnOffTvLight")   
            tuya.handle_request("?Upstairs_Off=On" )
            tradfri.handle_request("?TvRoomGroup=off" )
        else:
            pass
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
            return BaseService.get_html_gui(self, column_id)

        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        res = ""
        
        column  = column.replace("<SERVICE_VALUE>", "<li>"+res+"</li>\n")

        return column
    
    
if __name__ == '__main__':
    import davan.config.config_creator as configuration
    from davan.util import application_logger as log_manager
    
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = HarmonyService("", config)
    test.handle_request("?On")
    
 #   test.get_html_gui("0")
 