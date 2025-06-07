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
import inspect

from threading import Thread,Event

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
import davan.http.service.lawn.RobomoStates as states


class RobomowService(ReoccuringBaseService):
    '''
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self,constants.ROBOMOW_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.transition_time = 60 
        self.local_event = Event()
        self.local_event.set()

    def init_service(self):
        '''
        Create db table if not already present
        '''
        self.logger.info("Init RobomowService")
        self.transition_state = states.InactiveState(self)
        self.sm = StateMachine(self.config, self.transition_state)
        
    def get_next_timeout(self):
        '''
        Return time until next timeout.
        '''
        self.time_to_next_event =  self.sm.get_timeout()
        self.logger.debug("Next timeout in [" + str(self.time_to_next_event) +  "] seconds")
        return self.time_to_next_event
    
    def handle_timeout(self):
        '''
        handle timeout
        '''

        if isinstance(self.sm.currentState, states.WorkingState):
            self.sm.handle_timeout()
        elif isinstance(self.sm.currentState, states.ChargingState):
            self.sm.handle_timeout()
        

    def parse_request(self, msg):
        '''
        '''
        msg = msg.split('?')
        res = msg[1].split('=')
        return res[0],res[1]


    def handle_request(self, msg):
        '''
        '''
        try:
            reqType, value = self.parse_request(msg)
            self.logger.debug("Request[" + msg +"] ReqType["+reqType+"] Value["+value+"]")
            self.increment_invoked()

            if reqType =="service":
               if value == constants.TURN_ON:
                    self.logger.info("Changing state to Active state")
                    self.sm.change_state(states.ActiveState(self))                                          
               else:
                    self.logger.info("Changing state to inactive state")                    
                    self.sm.change_state(states.InactiveState(self))                                          
            else:
                self.sm.handle_data( value )
                next = self.sm.next()
                if next:
                    self.handle_transition(next)
        except Exception:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")
    
    def handle_transition(self, next_state):
        next_state_name = next_state.__class__.__name__ 
        if  self.local_event.is_set():
            self.logger.info("Start state transition to [" + next_state_name +"]")
            self.transition_state = next_state
            self.start_transition(next_state)
        else:
            self.logger.info("Transition already started")
            if next_state_name != self.transition_state.__class__.__name__ :
                self.logger.info("Restart transition to new state: "+ next_state_name)
                self.transition_state = next_state
                self.cancel_transition()
                self.start_transition(next_state)
            else:
                self.logger.info("Continue transition to state :" + next_state_name )                

    def start_transition(self, next_state):
        '''
        Start state transition
        '''
        self.local_event = Event()
        def countdown():
            try:                    
                self.increment_invoked()
                # Wait x seconds before actually changing state
                while not self.local_event.wait(self.transition_time):
                    self.perform_transition(next_state)
            except:
                self.logger.error(traceback.format_exc())
                self.increment_errors()

        Thread(target=countdown, name="RobmowTransitionTimer").start()    
        return self.local_event.set

    def perform_transition(self, next_state):
        self.sm.change_state(next_state)
        self.local_event.set()

    def cancel_transition(self):
        '''
        State changed before transition timer
        '''
        self.logger.info("State changed during transition time")
        self.local_event.set()


    def send_notification(self, message):
        helper.send_telegram_message(self.config, message)


    def update_fibaro_device(self, activity_counter, message):
        '''
        Update virtual device with current state and time when state changed.
        '''
        time_changed , _ ,current_date = timer_functions.get_time_and_day_and_date()

        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROBOMOW_ID_1'],
                                self.config['FIBARO_VD_ROBOMOW_MAPPINGS_1']['Date'],
                                current_date)
        helper.send_auth_request(url,self.config)

        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROBOMOW_ID_1'],
                                self.config['FIBARO_VD_ROBOMOW_MAPPINGS_1']['Status'],
                                message)
        self.logger.info("Url 1: " +str(url))
        helper.send_auth_request(url,self.config)

        value = time_changed + "   " +message
        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROBOMOW_ID_1'],
                                self.config['FIBARO_VD_ROBOMOW_MAPPINGS_1']['Activity'],
                                value)
        url = url.replace('<id>',str(activity_counter))                                

        helper.send_auth_request(url,self.config)

    def reset_fibaro_device(self):
        max_number_of_activities = 14
        _ , _ ,current_date = timer_functions.get_time_and_day_and_date()


        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROBOMOW_ID_1'],
                                self.config['FIBARO_VD_ROBOMOW_MAPPINGS_1']['Date'],
                                current_date)
        helper.send_auth_request(url,self.config)

        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROBOMOW_ID_1'],
                                self.config['FIBARO_VD_ROBOMOW_MAPPINGS_1']['Status'],
                                "Active")
        helper.send_auth_request(url,self.config)

        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROBOMOW_ID_1'],
                                self.config['FIBARO_VD_ROBOMOW_MAPPINGS_1']['Date'],
                                current_date)
        helper.send_auth_request(url,self.config)

        for activity in range(max_number_of_activities):
            url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                    self.config['FIBARO_VD_ROBOMOW_ID_1'],
                                    self.config['FIBARO_VD_ROBOMOW_MAPPINGS_1']['Activity'],
                                    "")
            url = url.replace('<id>',str(activity))                                

            helper.send_auth_request(url,self.config)

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

        result = "State: " + str(self.sm.currentState.__class__.__name__) + "</br>\n"
         
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", result)
        return column
