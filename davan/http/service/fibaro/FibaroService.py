'''
@author: davandev
'''

import logging
import os
import json
import urllib.request, urllib.parse, urllib.error
import traceback

import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper
from davan.util import application_logger as log_manager
from davan.http.service.reoccuring_base_service import ReoccuringBaseService


class FibaroService(ReoccuringBaseService):
    '''
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self,constants.FIBARO_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        
        self.alarmStatus = {'Skalskydd':"-",'Alarm':'-','Garden':'-'}
        self.memory = {'Cache':"-",'Used':'-','Buffer':'-','Free':'-'}
        self.storage = {'System':"-",'Recovery':'-'}
        self.DISARMING = "Disarming"
        self.faulty_state = ""
    
    def do_self_test(self):
        try:
            helper.send_auth_request(self.config['FIBARO_API_ADDRESS'] + "diagnostics",self.config)
        except:
            self.logger.error(traceback.format_exc())

            msg = "Self test failed"
            self.logger.error(msg)
            self.raise_alarm(msg,"Warning",msg)

    def get_next_timeout(self):
        return self.config['FibaroTimeout']
                                             
    def handle_timeout(self):
        '''
        Timeout received, iterate all active scenes to check that they are running on fibaro 
        system, otherwise start them
        '''
        try:
            self.fetch_alarm_status()
            self.check_status()
        except Exception:
            helper.send_telegram_message(self.config, "Ingen kontakt med HC2 Fibaro")
            self.logger.error(traceback.format_exc())
            self.increment_errors()
    
    def fetch_diagnostics(self):
        '''
        Fetch and parse diagnostics from Fibaro system
        '''
        result = helper.send_auth_request(
            urllib.request.urlopen(self.config['FIBARO_API_ADDRESS'] + "diagnostics"),
            self.config)

        res = result.read()
        data = json.loads(res)
            
    def fetch_alarm_status(self):
        '''
        Fetch and parse alarm status
        '''
        result = helper.send_auth_request(
            self.config['FIBARO_API_ADDRESS'] + "devices?id=" + self.config['FibaroVirtualDeviceId'],
            self.config)

        res = result.read()
        data = json.loads(res)
        for key, value in data.items():
            if key == "properties":
                for k, v in value.items():
                    if k  == "ui.Label1.value":
                        self.alarmStatus["Skalskydd"] = str(v)
                    elif k == "ui.Label2.value":
                        self.alarmStatus["Alarm"] = str(v)
                    elif k == "ui.Label5.value":
                        self.alarmStatus["Garden"] = str(v)

    def check_status(self):
        for alarmType, alarmStatus in self.alarmStatus.items():
            if self.DISARMING in alarmStatus:
                
                helper.send_telegram_message(self.config, alarmType + " is in state " + alarmStatus)
                self.faulty_state = alarmType
    
    def print_status(self):
        self.logger.info(str(self.alarmStatus))
        
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

        result = "Skalskydd: " + str(self.alarmStatus["Skalskydd"]) + "</br>\n"
        result +="Alarm: " + str(self.alarmStatus["Alarm"]) + "</br>\n" 
        result +="Garden: " + str(self.alarmStatus["Garden"]) + "</br>\n"
         
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", result)
        return column