# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import logging
import os
import urllib.request, urllib.parse, urllib.error

from davan.http.service.base_service import BaseService
import davan.util.constants as constants
import davan.util.helper_functions as helper_functions

class DishWashService(BaseService):
    '''
    '''
    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.DISHWASH_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        
    
    def _parse_request(self,msg):
        self.logger.debug("Parse request:" + msg)
        msg = msg.replace("/DishWashService?status=finished", "")
        return urllib.parse.unquote(msg)
                
    def handle_request(self, msg):
        '''
        Received message from android device 
        '''
        self.increment_invoked()
        self.logger.debug("Received DishWashStatus ["+ msg + "]")
        msg = "Tvättmaskinen är färdig"
        self.services.get_service(constants.TTS_SERVICE_NAME).start(msg,constants.SPEAKER_KITCHEN)

        return constants.RESPONSE_OK, \
               constants.MIME_TYPE_HTML, \
               constants.RESPONSE_EMPTY_MSG.encode("utf-8")
