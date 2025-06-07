'''
@author: davandev
'''

import logging
import os
import urllib.request, urllib.error, urllib.parse, base64
import re

import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.http.service.base_service import BaseService

class AuthenticationService(BaseService):
    '''
    Service used to authenticate triggering (arm/disarm) of Fibaro home alarm via
    Android alarm keypad.
    Notice that Android alarm keypad can be configured to arm/disarm Fibaro alarm itself and 
    does not require request through this service
    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.AUTH_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.ok_rsp = 200
        self.nok_rsp = 401
        self.reg_exp_arm = re.compile(r'\/authenticate\?action=([A-Za-z]+)')
        self.reg_exp_disarm = re.compile(r'\/authenticate\?action=(.+?)\&pin=([0-9]+)')

    # Implementation of BasePlugin abstract methods        
    def handle_request(self, msg):
        '''
        Recevied request from Android keypad to authenticate
        user and arm/disarm alarm..
        '''
        self.logger.info("Received request for authentication")

        self.increment_invoked()
        action, pin = self.parse_request(msg)
        
        if action and not pin: # arm alarm
            if action == "armAlarm" or action == "armSkalskydd":
                self.perform_security_action(action)
                return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, ""
        
        elif action and pin: # disarm alarm, requires pin code
            user = self.authenticate_user(pin)
            if user == None:
                return constants.RESPONSE_NOT_OK, constants.MIME_TYPE_HTML,  ""            
            else:
                self.perform_security_action(action)
                return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, "{user:" + user + "}"

    def parse_request(self, msg):
        '''
        Return the interesting parts from the message, 
        @param msg, received msg
        @return user, pincode
        '''
        self.logger.info("Parse request:" + msg)
        match = self.reg_exp_disarm.search(msg)
        if match:
            return match.group(1), match.group(2)

        match = self.reg_exp_arm.search(msg)
        if match:
            return match.group(1), None
        
        return None, None
    
    def authenticate_user(self, pin):
        '''
        Verify that the pincode matches the configured pin code
        @param pin, pincode to verify
        @return the name of the user matching the pin code
        
        '''
        if pin in self.config['USER_PIN']:
            return self.config['USER_PIN'][pin]
        return None
        
    def perform_security_action(self, action):
        ''' 
        Create the url and perform arm/disarm of Fibaro system
        @param action, arm/disarm
        '''  
        
        if action in self.config:
            self.logger.debug("Action:" + self.config[action])
            request = urllib.request.Request(self.config[action])
            base64string = base64.encodestring(self.config["FIBARO_USER_NAME"] + ":" + 
                                               self.config["FIBARO_PASSWORD"])
            request.add_header("Authorization", "Basic %s" % base64string)   
            result = urllib.request.urlopen(request)    
            self.logger.info("Result: " + str(result) )
        
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = AuthenticationService()
    test.start("/authenticate?action=armSkalskydd")
