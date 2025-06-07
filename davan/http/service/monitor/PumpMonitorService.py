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
import davan.util.helper_functions as helper
from davan.util.StateMachine import StateMachine
from davan.util.StateMachine import State
import davan.util.timer_functions as timer_functions
from davan.http.service.db.PumpMonitorDbHandle import PumpMonitorDbHandle

class BaseState(State):
    def __init__(self, service,invoked):
        State.__init__( self )
        self.service = service
        self.nr_invocations = invoked
        self.value = ""

    def handle_data(self, value):
        self.service.logger.debug("Data: [" + value+ "]")
        self.value = value

class ActiveState(BaseState):
    def __init__(self, service, invoked):
        BaseState.__init__(self, service, invoked)
        self.nr_invocations = invoked
        self.nr_invocations += 1
        self.service.update_virtual_device( self.nr_invocations )

    def next(self):
        if self.value == "inactive":
           self.service.logger.debug("Change state to inactive")
           return InactiveState(self.service, self.nr_invocations)

    def get_message(self):
        if self.service.logger.getEffectiveLevel() == logging.INFO:
            return None

        return "Startar pump brunn [ "+str(self.nr_invocations)+" ]"

class InactiveState(BaseState):
    def __init__(self, service, invoked):
        BaseState.__init__(self, service, invoked)
        self.nr_invocations = invoked

    def next(self):
        if self.value == "active":
            self.service.logger.debug("Change state to active")
            return ActiveState(self.service, self.nr_invocations)

    def get_message(self):
        if self.service.logger.getEffectiveLevel() == logging.INFO:
            return None

        return "Stoppar pump brunnen"

class PumpMonitorService(ReoccuringBaseService):
    '''
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self,constants.PUMP_MONITOR_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.first_invoked = time.localtime()
        self.last_invoked = self.first_invoked
        self.max_wait = 0 

        self.interval = datetime.timedelta(seconds=120)
        self.db = PumpMonitorDbHandle( config )

    def init_service(self):
        '''
        Create db table if not already present
        '''
        self.db.init_db()
        res = self.db.read_last_entry()
        self.previous_invocations = res[0]
        self.interval = datetime.timedelta(seconds=res[1])

        self.logger.info("Invocation[" + str(self.previous_invocations) + "] Interval[" + str(self.interval) + "]")
        self.sm = StateMachine(self.config, InactiveState(self, self.previous_invocations))
        

    def get_next_timeout(self):
        '''
        Return time until next timeout, only once per day.
        '''
        self.time_to_next_event =  self.interval.total_seconds() + self.max_wait
        self.logger.debug("Next timeout in [" + str(self.time_to_next_event) +  "] seconds")
        return self.time_to_next_event
    
    def handle_timeout(self):
        '''
        '''
        if self.sm.currentState.nr_invocations <= 1:
           self.logger.info("Not yet invoked or not enough data")
           return
        

        if self.sm.currentState.nr_invocations != self.previous_invocations:
           self.logger.debug("Pumpbrunn has been invoked during last timeout")
        else:
           self.logger.warning("Pumpbrunn NOT invoked!!")
           msg = "Intervallet ["+str(self.interval)+ "] för pumpbrunnen har passerats ["+str(self.last_invoked)+"]"
           helper.send_telegram_message(self.config, msg)

        # Set max time to wait before reporting
        self.max_wait = 60*15 
        self.previous_invocations = self.sm.currentState.nr_invocations


    def handle_request(self, msg):
        '''
        '''
        try:
            msg = msg.replace("/PumpMonitorService?", "")

            self.sm.handle_data( msg )
            next = self.sm.next()
            if next:
                self.sm.change_state(next)
            self.increment_invoked()

        except Exception:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")

    def update_virtual_device(self, invoked):
        volume = invoked * 20 
        self.config['FIBARO_VD_PUMP_MAP']['volume']
        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_PUMP_ID'],
                                self.config['FIBARO_VD_PUMP_MAP']['volume'],
                                str(volume))

        helper.send_auth_request(url,self.config)
        now = time.localtime()
        self.interval = datetime.timedelta(seconds=time.mktime(now) - time.mktime(self.last_invoked))
        self.last_invoked = now
        
        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_PUMP_ID'],
                                self.config['FIBARO_VD_PUMP_MAP']['date'],
                                str(time.strftime("%Y-%m-%d %H:%M", now)))
        helper.send_auth_request(url,self.config)

        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_PUMP_ID'],
                                self.config['FIBARO_VD_PUMP_MAP']['interval'],
                                str(self.interval))
        helper.send_auth_request(url,self.config)
        
        self.db.insert(invoked, self.interval.total_seconds() )
                       
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
        volume = self.sm.currentState.nr_invocations * 20 

        result = "Volym: " + str(volume) + "</br>\n"
        result +="Startad: " + str(self.first_invoked) + "</br>\n" 
        result +="Senast tömd: " + str(self.last_invoked) + "</br>\n" 
        result +="Interval: " + str(self.interval) + "</br>\n" 
        result +="Tömningar: " + str(self.previous_invocations) + "</br>\n" 
         
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", result)
        return column
