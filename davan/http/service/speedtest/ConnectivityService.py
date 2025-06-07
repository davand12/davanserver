# -*- coding: utf-8 -*-
'''
@author: davandev
'''
import datetime
        
import logging
import os
import json
import re
import time
import traceback
from datetime import date

import davan.config.config_creator as configuration
import davan.util.cmd_executor as cmd
import davan.util.constants as constants
import davan.util.helper_functions as helper
from davan.http.service.reoccuring_base_service import ReoccuringBaseService
from davan.util.StateMachine import StateMachine
from  davan.util.StateMachine import State

class Connected(State):
    def __init__(self,  connService , servicesRunning=False):
        State.__init__( self)
        self.connected = True
        self.service = connService

        if not servicesRunning:
            self.service.toggle_services(True)

    def handle_data(self, connection_result):
        if not self.service.is_connection_established(connection_result):
            self.connected = False

    def next(self):
        if not self.connected:
            return Disconnecting(self.service)
        return None

    def get_message(self):
        return "Internet är tillbaka"

class Disconnecting(State):
    def __init__(self, connService):
        State.__init__( self )
        self.lost_count = 0
        self.service = connService
        self.lost_limit = 5
        self.disconnected = False
        self.connected = False

    def handle_data(self, connection_result):
        self.logger.info("Check connection state:["+str(connection_result)+"]")

        if self.service.is_connection_established(connection_result):
            self.connected = True
        else:
            self.lost_count += 1
            if self.lost_count >= self.lost_limit:
                self.disconnected = True

    def next(self):
        if self.disconnected:
            return Disconnected(self.service)
        if self.connected:
            return Connected(self.service, servicesRunning=True)


        return None

    def get_message(self):
        return None

class Disconnected(State):
    def __init__(self, connService):
        State.__init__( self )
        self.connected = False
        self.service = connService
        self.service.toggle_services(False)

    def handle_data(self, connection_result):
        self.logger.info("Check connection state:["+str(connection_result)+"]")

        if self.service.is_connection_established(connection_result):
            self.connected = True

    def next(self):
        if self.connected:
            return Connected(self.service)
        return None

    def get_message(self):
        return "Internet är borta"


class ConnectivityService(ReoccuringBaseService):
    '''
    Starts a re-occuring service that will check connection connectivity"
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.CONNECTIVITY_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.command = "ping -c 1 www.google.com"
        self.time_to_next_timeout = 60
    
    def init_service(self):
        self.sm = StateMachine(self.config, Connected(self, True))

    def handle_request(self, msg):
        '''
        Received request for the latest speedtest measurements.
        '''
        self.logger.info("Receive Msg:"+msg)
        if "StopServices" in msg:
            self.logger.info("Disable services")
            self.is_enabled = False
        if "StartServices" in msg:
            self.logger.info("Enable services")
            self.is_enabled = True

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")

    def is_connection_established(self, connection_string):
        if not connection_string:
            return False

        disconnected_strings=[" 100% packet loss", "Temporary failure in name resolution"]
        for failure_string in disconnected_strings:
            if failure_string in connection_string:
                return False
        return True

    def toggle_services(self,enable):
        self.logger.info("Toggle services["+str(enable)+"]")
        if enable:
            self.services.start_all_except(self.get_name())
        else:
            self.services.stop_all_except(self.get_name())

    def handle_timeout(self):
        self.logger.debug("Check internet connectivity")
        try:
            if self.is_enabled == False: # Manually disabled
                result =" 100% packet loss Temporary failure "
            else:
                result = cmd.execute_block(self.command, "ConnectivityTest", True)
        except:
            self.logger.warning("Failed to perform ping.. : " + str(result) )
            self.logger.error(traceback.format_exc())
            self.increment_errors()        
        
        self.sm.handle_data(result)
        next_state = self.sm.next() 
        
        if next_state:
            self.sm.change_state(next_state)     

    def get_next_timeout(self):
        '''
        Return time to next speed measuring
        '''
        self.logger.debug("Next timeout:"+ str(self.time_to_next_timeout))
        return self.time_to_next_timeout

if __name__ == '__main__':
    from davan.util import application_logger as log_config
    import time
    
    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = ConnectivityService("",config)
    current_time = datetime.datetime.now().strftime('%H:%M')
    test.disconnected_at = datetime.datetime.now().strptime(current_time, '%H:%M')
    
    time.sleep(70)
    current_time = datetime.datetime.now().strftime('%H:%M')
    test.connected_at = datetime.datetime.now().strptime(current_time, '%H:%M')
    test.report_down_time()
