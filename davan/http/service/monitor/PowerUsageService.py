# -*- coding: utf-8 -*- 
'''
@author: davandev
'''

import logging
import os
import traceback
import sys
import time

import davan.util.timer_functions as timer_functions
import davan.util.helper_functions as helper
import davan.config.config_creator as configuration
import davan.util.constants as constants

from davan.http.service.reoccuring_base_service import ReoccuringBaseService
from threading import Thread,Event

class PowerUsageService(ReoccuringBaseService):
    '''
    Monitor usage of a device controlled by a powerplug. 
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self,constants.POWER_USAGE_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.start_time =""
        self.stop_time= ""
        self.configured_usage_time = 3600
        self.local_event = None
        self.timeleft = self.configured_usage_time
        self.actual_usage_time = 0
        self.current_status = "Off"
    
    def get_next_timeout(self):
        '''
        Return time until next timeout, only once per day.
        '''
        self.time_to_next_event = timer_functions.calculate_time_until_midnight()
        self.logger.debug("Next timeout in " + str(self.time_to_next_event) +  " seconds")
        return self.time_to_next_event
    
    def handle_timeout(self):
        '''
        Reset the time to play every night 
        '''
        self.logger.info("Resetting play monitor")
        self.timeleft = self.configured_usage_time
        self.actual_usage_time = 0
        
    def handle_request(self, msg):
        '''
        '''
        try:
            self.increment_invoked()
            state = self.parse_request(msg)
            self.logger.debug("State = " + state)
            if state.lower() == "on":
                self.start_count_down()
            else:
                self.stop_count_down()
        except:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            self.logger.error("Failed to handle power usage request")
            return constants.RESPONSE_NOT_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_FAILED_TO_PARSE_REQUEST
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")

    def start_count_down(self):
        
        self.logger.info("Starting timer, time left [ "+str(self.timeleft)+" ]")
        self.current_status = "On"
        self.local_event = Event()
        self.start_time = time.time()

        def countdown():
            try:                    
                self.increment_invoked()
                while not self.local_event.wait(self.timeleft):
                    self.time_is_out()
            except:
                self.logger.error(traceback.format_exc())
                self.increment_errors()

        Thread(target=countdown).start()    
        return self.local_event.set
    
    def stop_count_down(self):
        '''
        Manual stop of count down
        '''
        self.logger.info("Stopping timer")
        self.local_event.set()
        self.current_status = "Off"

        self.stop_time = time.time()
        diff = self.stop_time - self.start_time
        if (diff<self.timeleft):
            self.timeleft -=diff 
        else:
            self.timeleft = 0
        
        self.actual_usage_time += diff
        self.logger.debug("Time left[ " + str(self.timeleft) + " ] Usage time[" + str(self.actual_usage_time) + "]")
        
    def time_is_out(self):
        '''
        Callback function when time is out
        '''
        self.logger.info("Time is out!")
        self.local_event.set()
        self.timeleft = 0
        self.actual_usage_time = self.configured_usage_time
        # Restart time measurement when timeleft == 0
        self.start_time = time.time()
        
        msg = "Viggo har nu använt upp all sin speltid"
        
        helper.send_telegram_message(self.config, msg)
        self.services.get_service(
            constants.TTS_SERVICE_NAME).start(msg,constants.SPEAKER_KITCHEN)

        
    def parse_request(self, msg):
        '''
        Return camera name from received msg.
        '''
        self.logger.debug("Parsing: " + msg ) 
        msg = msg.replace("/PowerUsageService?device=1&state=", "")
        return msg


    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, column_id):
        """
        Override and provide gui
        """
        if self.actual_usage_time > 60: 
            usage = str(self.actual_usage_time/60)
        else:
            usage = self.actual_usage_time
            
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        
        htmlresult = "<li>Status: " + str(self.current_status) + "</li>\n"
        htmlresult += "<li>Time left: " + str(self.timeleft) + "</li>\n"
        htmlresult += "<li>Actual usage: " + str(usage) + "</li>\n"
        column = column.replace("<SERVICE_VALUE>", htmlresult)

        return column

    def get_announcement(self):
        '''
        Compose and encode announcement data
        '''
        self.logger.info("Create powerusage announcement")
        
        announcement = "Viggo, du har "
        announcement += str(self.timeleft) 
        announcement += " sekunder kvar att spela idag"
        announcement = " och du har spelat totalt"
        announcement += str(self.timeleft/60) 
        announcement += " minuter idag "
        return announcement

if __name__ == '__main__':
    import time
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = PowerUsageService("",config)
    test.handle_request("/PowerUsageService?device=1&state=On")
    time.sleep(90)
