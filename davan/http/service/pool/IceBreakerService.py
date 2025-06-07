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
import time
import datetime

import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper
from davan.util import application_logger as log_manager
from davan.http.service.reoccuring_base_service import ReoccuringBaseService
from davan.util.StateMachine import StateMachine
from davan.util.StateMachine import State
import davan.util.timer_functions as timer_functions
import davan.util.constants as constants

class BaseState(State):
    def __init__(self, service, invoked):
        State.__init__( self )
        self.service = service
        self.nr_invocations = invoked
        self.value = ""
        self.timeout_time = -1

    def handle_data(self, value):
        self.service.logger.debug("Temp: [" + str(value)+ "]")
        self.value = value

class WorkingState(BaseState):
    def __init__(self, service, invoked):
        BaseState.__init__(self, service, invoked)
        self.nr_invocations = invoked
        self.nr_invocations += 1

    def next(self):
        self.service.logger.info("Change state to WaitingState")
        return WaitingState(self.service, self.nr_invocations)

    def get_message(self):
        return "Cirkulerar poolvatten [ "+str(self.nr_invocations)+" ]"
    
    def get_timeout(self):
        '''
        Run for 3 minutes
        '''
        self.timeout_time = timer_functions.get_time(180)

        return 180

    def enter(self):
        self.service.logger.info("Starting water pump")
        self.service.toggle_controller(True)

    def exit(self):
        self.service.toggle_controller(False)


class WaitingState(BaseState):
    def __init__(self, service, invoked):
        BaseState.__init__(self, service, invoked)
        self.nr_invocations = invoked

    def next(self):
        if int(self.value) < 0:
           self.service.logger.info("Change state to WorkingState")
           return WorkingState(self.service, self.nr_invocations)
        else:
           self.service.logger.info("Currently warmer than 0 degree")

    def get_message(self):
        return "Ingen cirkulation av poolvatten"

    def get_timeout(self):
        '''
        Get number of seconds until next hour
        '''
        wait_seconds = timer_functions.get_seconds_to_next_hour()
        self.timeout_time = timer_functions.get_time(wait_seconds)

        return wait_seconds
    
    def enter(self):
        self.service.logger.info("Stopping water pump")
        self.service.toggle_controller(False)


class IceBreakerService(ReoccuringBaseService):
    '''
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self,constants.ICE_BREAKER_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.last_invoked = time.localtime()
        self.sm = StateMachine(config, WaitingState(self,0))

    def get_next_timeout(self):
        '''
        Return time until next timeout.
        '''
        return self.sm.get_timeout()
    
    def handle_timeout(self):
        '''
        Fetch current temp, invoke and execute state 
        '''
        current_temp = self.services.get_service( constants.ECOWITT_SERVICE_NAME ).get_data( 'tempc' )
        self.logger.info("Timeout! Current temp: "+ str(current_temp))
        self.sm.handle_data( current_temp )
        next = self.sm.next()
        if next:
           self.sm.change_state(next)
        self.increment_invoked()

    def toggle_controller(self, enable):
        '''
        Toggle power controller
        '''
        action = constants.TURN_OFF
        if enable:
           action = constants.TURN_ON

        url = helper.create_fibaro_url_set_device_value(
                self.config['DEVICE_SET_VALUE_URL'], 
                self.config['ICEBREAKER_ID'],
                action)

        self.logger.info("URL:"+url)
        helper.send_auth_request(url,self.config)

    def handle_request(self, msg):
        '''
        '''
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
            return ReoccuringBaseService.get_html_gui(self, column_id)
        msg = self.sm.currentState.get_message()

        result = "Status: " + msg + "</br>\n"
        result +="Temperatur: " + str(self.sm.currentState.value) + "</br>\n" 
        result +="Timeout: " + str(self.sm.currentState.timeout_time) + "</br>\n" 
         
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", result)
        return column
