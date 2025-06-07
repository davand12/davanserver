# -*- coding: utf-8 -*-

'''
@author: davandev
'''

import logging
import os
import traceback
import sys
import urllib.request, urllib.parse, urllib.error
import json

import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.util import cmd_executor as cmd_executor
from davan.http.service.base_service import BaseService
import davan.util.helper_functions as helper


class ExternalEventService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,constants.EXTERNAL_EVENT_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.payload="/ExternalEventService="
        self.enable_notifications = True
        self.enable_pictures = True
              
    def parse_request(self, msg):
        '''
        Parse received request to get interesting parts
        @param msg: received request 
        '''
        msg = msg.replace(self.payload, "")
        return msg
             
    def handle_request(self, msg):
        '''
        '''
        try:
            msg = self.parse_request(msg)
            self.logger.debug("Received: " + msg ) 
            
            self.increment_invoked()
            
            if msg == "enable_notifications":
                self.enable_notifications = True
                helper.send_telegram_message(self.config, "Börjar skicka meddelanden")
                return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, ""
            elif msg == "disable_notifications":
                self.enable_notifications = False
                helper.send_telegram_message(self.config, "Slutar skicka meddelanden")
                return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, ""
            if msg == "enable_pictures":
                self.enable_pictures = True
                helper.send_telegram_message(self.config, "Börjar skicka bilder")
                return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, ""
            elif msg == "disable_pictures":
                self.enable_pictures = False
                helper.send_telegram_message(self.config, "Slutar skicka bilder")
                return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, ""
            
            if self.enable_notifications :
                if msg == "ytter_door_opened":
                    helper.send_telegram_message(self.config, "Ytterdörren öppnades")
                elif msg == "ytter_door_closed":
                    helper.send_telegram_message(self.config, "Ytterdörren stängdes")
                elif msg == "basement_door_closed":
                    helper.send_telegram_message(self.config, "Källardörren stängdes")
                elif msg == "basement_door_opened":
                    helper.send_telegram_message(self.config, "Källardörren öppnades")
                elif msg == "door_3_opened":
                    helper.send_telegram_message(self.config, "Dörr 3 öppnades")
                elif msg == "door_3_closed":
                    helper.send_telegram_message(self.config, "Dörr 3 stängdes")
            
            if self.enable_pictures:
                if msg == "motion":
                    self.services.get_service(
                        constants.PICTURE_SERVICE_NAME).take_and_send_picture("SsundFramsida")
            result =""

            return constants.RESPONSE_OK, \
                constants.MIME_TYPE_HTML, \
                constants.RESPONSE_EMPTY_MSG.encode("utf-8")

        except:
            self.logger.info("Failed to carry out ups request")
            self.increment_errors()
            traceback.print_exc(sys.exc_info())
 
    
    def has_html_gui(self):
        """
        Override if service has gui
        """
        return False
    
    def get_html_gui(self, column_id):
        """
        Override and provide gui
        """
        if not self.is_enabled():
            return BaseService.get_html_gui(self, column_id)
                
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    upspath = "/Ups?text=Status"
    test = ExternalEventService()
    test.start(upspath)
