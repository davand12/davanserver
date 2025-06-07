'''
@author: davandev
'''

import logging
import os

import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.util import application_logger as log_manager
from davan.http.service.base_service import BaseService

import hashlib
       
class AlarmService(BaseService):
    '''
    '''
    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.ALARM_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.alarms = {}

    def raise_alarm(self, alarm):
        self.logger.info("Adding new alarm "+ alarm.toString())
        self.alarms[alarm.id] = alarm 
        
    def clear_alarm(self, alarm):
        alarmkey = hashlib.md5(alarm).hexdigest()
        self.logger.info("Clear alarm [" + alarmkey + "]")
        if alarmkey in self.alarms:
            self.alarms.pop(alarmkey)

    def get_alarms(self, Alarm):
        return self.alarms
        
    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, column_id):
        """
        Override and provide gui
        """
        
        result = "Active alarms:</br>\n"
        for value in list(self.alarms.values()):
            result += value.toString() + "</br>\n"
         
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", result)
        return column