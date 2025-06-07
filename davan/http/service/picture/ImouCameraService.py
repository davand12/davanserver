# -*- coding: utf-8 -*- 
'''
@author: davandev
'''

import logging
import os
import traceback
import sys
from urllib.parse import urlparse
import json

import davan.config.config_creator as configuration
import davan.util.constants as constants

from davan.util import cmd_executor as cmd_executor
from davan.http.service.base_service import BaseService
from davan.util.StateMachine import StateMachine
from davan.util.StateMachine import State
from davan.http.service.picture.ImouCameraHandle import ImouCameraHandle

class ImouCameraService(BaseService):
    '''
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.IMOU_CAMERA_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        #self.app_id= config['IMOU_APPID'] #"lcfb0ddc13ada74f5a"
        #self.app_secret= config['IMOU_SECRET'] #"9b507c0a583f4352a605f56a9991c2"
        self.cameras = {'Framsidan' : ImouCameraHandle(self.config, self.services, 'Framsidan'),
        'Parkering' : ImouCameraHandle(self.config, self.services, 'Parkering'),
        'Balkong' : ImouCameraHandle(self.config, self.services, 'Balkong'),
        'Baksidan' : ImouCameraHandle(self.config, self.services, 'Baksidan'),
        }

    def do_self_test(self):
        self.logger.info("Perform self test")
        pass
        
    def handle_request(self, msg):
        try:
            #self.logger.info("Received request: " + str(msg))
            camera, data = self.parse_request(msg)
            
            if not camera in self.cameras:
                self.logger.info("Received request to unknown camera")
                return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")

            self.cameras[camera].handle_data(data)

        except Exception as ex:
           self.logger.info("Caught exception " + str(ex))
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")


    def parse_request(self, msg):
        try:
            data = json.loads(msg)
            self.logger.info("data:" + str(data))
            if 'cname' in data:
                return data['cname'], data
        except Exception as ex:
           self.logger.info("Caught exception parsing["+str(msg)+"]" + str(ex))
        return None, data


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
        column = column.replace("<SERVICE_VALUE>", "<li>Cameras: " + str(list(self.config["CAMERAS"].keys())) + " </li>\n")
        return column
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = ImouCameraService(None,config)
