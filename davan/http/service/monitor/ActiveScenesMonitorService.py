'''
@author: davandev
'''

import logging
import os
import json
import urllib.request, urllib.parse, urllib.error
import traceback
from threading import Thread,Event

import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper

from davan.util import application_logger as log_manager
from davan.http.service.reoccuring_base_service import ReoccuringBaseService


class ActiveScenesMonitorService(ReoccuringBaseService):
    '''
    Monitor active scenes on Fibaro system, in some cases
    scenes that should always be running are stopped.
    Check status of each active scene and start it if stopped. 
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self,constants.ACTIVE_SCENES_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.time_to_next_timeout = 900
        self.restarts = 0
        
    def get_next_timeout(self):
        return self.time_to_next_timeout
                                             
    def handle_timeout(self):
        '''
        Timeout received, iterate all active scenes to check that they are running on fibaro 
        system, otherwise start them
        '''
        try:
            for scene in self.config['MONITOR_SCENES']:
                url = self.config['GET_STATE_SCENE_URL'].replace("<ID>",scene)
                self.logger.debug("Check state of " + scene)
                result = helper.send_auth_request(url, self.config)
                res = result.read()

                data = json.loads(res)
                if data["runningInstances"] == 1:
                    pass
                else:
                    self.logger.info("Scene not running")
                    self.logger.debug("Result:" + str(res))    
                    scene_url = self.config['START_SCENE_URL'].replace("<ID>",scene)
                    self.logger.info("Starting scene " + scene_url)
                    self.restarts += 1
                    result = helper.send_auth_request(scene_url, self.config)
        except Exception:
            self.logger.error(traceback.format_exc())
            self.increment_errors()

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
        
        result = "Monitor: " + str(self.config['MONITOR_SCENES']) + " </br>\n"
        result += "Nr of restarts[" +str(self.restarts)+"]</br>\n" 
        column = column.replace("<SERVICE_VALUE>", str(result))
        return column