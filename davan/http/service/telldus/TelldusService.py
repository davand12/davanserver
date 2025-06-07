'''
@author: davandev
'''

import logging
import os
import traceback

import davan.config.config_creator as configuration
import davan.http.service.telldus.tellduslive as telldus
import davan.util.constants as constants
from davan.http.service.base_service import BaseService
import davan.util.helper_functions as helper
from davan.http.service.telldus import tdtool


class TelldusService(BaseService):
    '''
    Telldus service, acts as a proxy between Fibaro system and Telldus Live.
    Forwards on/off triggering of lights from Fibaro system towards Telldus Live
    '''
    
    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.TELLDUS_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.STATES = {"on":1 , "off":2 , "toggle":3, "bell":4 }
    
    def init_service(self):
        self.session = telldus.Session(        
            self.config['TELLDUS_PUBLIC_KEY'],
            self.config['TELLDUS_PRIVATE_KEY'],
            self.config['TELLDUS_TOKEN'],
            self.config['TELLDUS_TOKEN_SECRET'])

    def do_self_test(self):
        self.session.update()
        for device in self.session.devices:
            print(device)
            for item in device.items:
                print("- {}".format(item))

    def start_service(self):
        self.is_running = True
        pass

    def parse_request(self, msg):
        '''
        Strip received request from uninteresting parts
        Example msg :"telldus?122379=on"
        @param msg, received request
        '''
        msg = msg.split('?')
        res = msg[1].split('=')
        return res[0], res[1]
            
    def handle_request(self, msg):
        '''
        Light on/off request received from Fibaro system,
        forward to Telldus Live.
        '''
        try:
            self.session.update()

            deviceId, action = self.parse_request(msg)
            self.increment_invoked()
            
            if deviceId == "all":
                action = self.STATES[action]
                self.toggle_all_device_states(action)
                return
            else:
                device = self.session.device(deviceId)
                self.execute_action(device, action)
            
            self.logger.info("DeviceId[" +deviceId+ "] Action[" + str(action)+"]")
        except:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            helper.send_telegram_message(self.config, "Telldus svarar inte") 
            self.raise_alarm(constants.TELLDUS_NOT_ANSWERING, "Warning", constants.TELLDUS_NOT_ANSWERING)

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")
    
    def execute_action(self, device, action):
        if action == "on" or action == "bell":
            device.turn_on()
        elif action == "off":
            device.turn_off()
        elif action == "toggle":
            if device.is_on:
                device.turn_off()
            else:
                device.turn_on()
        else:
            pass
    
    
    def list_all_devices(self):
        '''
        List all devices configured in Telldus Live
        '''
        self.logger.info("List all Telldus devices")
        self.session.update()
        for device in self.session.devices:
            self.logger.info(device)
            for item in device.items:
                self.logger.info("- {}".format(item))
        
if __name__ == '__main__':
    from davan.util import application_logger as app_logger
    config = configuration.create()
    
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = TelldusService("",config)
    test.list_all_devices()
