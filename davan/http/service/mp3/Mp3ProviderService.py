# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import logging
import os
import traceback

import davan.config.config_creator as configuration
import davan.util.constants as constants

from davan.http.service.base_service import BaseService

class Mp3ProviderService(BaseService):
    '''
    classdocs
    '''
    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.MP3_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
            
    def handle_request(self, msg):
        '''
        Received request for mp3 file.
        Verify that the mp3 file exist and return it
        @param msg, the wanted file.
        '''
        try:
            self.increment_invoked()
            self.logger.info("Received service request for file[" + msg + "]")
            res = msg.split('=')
            #with open(self.config['MP3_ROOT_FOLDER'] + res[1], encoding="utf8", errors='ignore') as f:

            f = open(self.config['MP3_ROOT_FOLDER'] + res[1], 'rb')
            content = f.read()
            f.close()
            return constants.RESPONSE_OK, self.get_content_type(res[1]), content
        except Exception as e:
            self.logger.error(str(e))
            self.logger.error(traceback.format_exc())

            self.increment_errors()
            self.logger.warning("Failed to open file: " + self.config['MP3_ROOT_FOLDER'] + res[1])
            return constants.RESPONSE_NOT_OK, constants.RESPONSE_FILE_NOT_FOUND
        
    def get_content_type(self, requested_file):
        if (requested_file.endswith(constants.OGG_EXTENSION)):
            self.logger.debug("Received ogg request")
            return constants.MIME_TYPE_OGG

        elif (requested_file.endswith(constants.WAV_EXTENSION)):
            self.logger.debug("Received wav request")
            return constants.MIME_TYPE_WAV
        else: 
            return constants.MIME_TYPE_MP3