# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import logging
import os
import traceback

import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper

from davan.http.service.base_service import BaseService

class DoorbellService(BaseService):
    '''
    classdocs
    '''
    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.DOORBELL_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
            
    def handle_request(self, msg):
        '''
        Received request from homeassistant that somebody pressed doorbell.
        '''
        self.increment_invoked()
        self.logger.info("Received doorbell notification")
        helper.send_telegram_message(self.config, "Ringklockan har tryckts")
        self.services.get_service(
            constants.PICTURE_SERVICE_NAME).take_and_send_picture("Farstukvist")
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")
