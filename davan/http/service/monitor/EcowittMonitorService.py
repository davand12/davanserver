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


class EcowittMonitorService(ReoccuringBaseService):
    '''
    Monitor ecowitt gateway
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self,constants.ECOWITT_MONITOR_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.time_to_next_timeout = 180
        self.restart_timeout = 30
        self.is_restarting = False
        self.restarts = 0
        self.socket_cmd = "/TradfriService?EcowittGateway=toggle"
        
    def get_next_timeout(self):
        if self.is_restarting:
            return self.restart_timeout

        return self.time_to_next_timeout
                                             
    def handle_timeout(self):
        '''
        Timeout received, iterate all active scenes to check that they are running on fibaro 
        system, otherwise start them
        '''
        try:
            if self.is_restarting:
                self.logger.info("EcowittGateway is restarted")
                self.is_restarting = False
                self.toggle_socket_controller()
                self.restarts +=1

            elif not self.services.get_service( constants.ECOWITT_SERVICE_NAME ).is_request_received():
                self.logger.info("EcowittService is not responding !!!")
                self.is_restarting = True
                self.toggle_socket_controller()
            else:
                pass

        except Exception:
            self.logger.error(traceback.format_exc())
            self.increment_errors()

    def toggle_socket_controller(self):
        self.logger.info("Toggle socket controller")
        
        self.services.get_service( constants.TRADFRI_SERVICE_NAME ).handle_request( self.socket_cmd )

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
        
        result = "Nr of restarts[" +str(self.restarts)+"]</br>\n" 
        column = column.replace("<SERVICE_VALUE>", str(result))
        return column