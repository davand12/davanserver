# -*- coding: utf-8 -*-

'''
@author: davandev
'''
import logging
import os
import json
import urllib.request, urllib.parse, urllib.error

import davan.util.cmd_executor as executor
import davan.util.constants as constants
import davan.util.helper_functions as helper_functions
from davan.http.service.reoccuring_base_service import ReoccuringBaseService

class TvService(ReoccuringBaseService):
    '''
    classdocs
    sys.setdefaultencoding('latin-1')
     aioharmony --harmony_ip 192.168.2.143 start_activity --activity 26681450
     aioharmony --harmony_ip 192.168.2.143 power_off
     aioharmony --harmony_ip 192.168.2.143 show_config
     http://192.168.2.173/api/statusinfo
    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.TV_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        
        self.base_cmd = "aioharmony --harmony_ip "
        self.start_activity_cmd = ' start_activity --activity '
        self.stop_activity_cmd = ' power_off'
        self.current_activity_cmd = ' show_current_activity'
        #self.watch_tv_activity = '26681450'
        self.vu_status_cmd ='http://192.168.2.173/api/statusinfo'
        self.status = "Off"
        self.standby = "-"
        self.channel = "-"
        self.program = "-"
        self.program_begin = "-"
        self.program_end = "-"
        self.program_desc = "-"

    def parse_request(self, msg):
        '''
        Strip received request from uninteresting parts
        Example msg :"telldus?122379=on"
        @param msg, received request
        '''
        res = msg.split('=')
        return res[1]

    def handle_request(self, msg):
        action = self.parse_request(msg)
        self.logger.info("Received request ["+action+"]")
        if action == "off":
            self.enable(False)
        else:
            self.enable(True)
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")
            
    def handle_timeout(self):
        '''
        '''
        self.check_tv_status()
        if self.status == "On":
            self.get_current_service_info()
        else:
            self.reset_service_info()
            
    def get_next_timeout(self):
        '''
        Return time until next timeout, only once per day.
        '''
        return self.config['TvServiceTimeout']
        
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
        res = "TV status:" +self.status + "\n"
        res += "Vu standby:" +str(self.standby) + "\n"
        res += "Channel:" +self.channel + "\n"
        res += "Program:" +self.program+ "\n"
        res += "" +self.program_begin+ "-" + self.program_end+"\n"
        res += "" +self.program_desc+ "\n"
        
        column  = column.replace("<SERVICE_VALUE>", "<li>"+res+"</li>\n")

        return column
    
    def enable(self, enable):
        '''
        Enable or disable tv activity
        '''
        cmd = self.base_cmd + self.config['HARMONY_IP_ADRESS']
        self.logger.info("Enable tv activity [" + str(enable) + "]")
        
        if enable == True:
            cmd += self.start_activity_cmd
            cmd += self.config['WATCH_TV_ACTIVITY']
            self.logger.debug("cmd:"+str(cmd))
            executor.execute_block(cmd, 'Harmony')
            self.status = "On"
        else:
            cmd += self.stop_activity_cmd
            executor.execute_block(cmd, 'Harmony')
            self.status = "Off"
            
    def check_tv_status(self):
        '''
        Check status of harmony tv activity.
        '''
        cmd = str(self.base_cmd)
        cmd += str(self.config['HARMONY_IP_ADRESS'] + " ")
        cmd += self.current_activity_cmd
        result = executor.execute_block(cmd, 'Harmony', True).strip()

        if 'PowerOff' in result:
            self.status = 'Off'
        elif 'Watch TV' in result:
            self.status = 'On'
        else:
            self.logger.warning("Unknown activity")
            self.status = 'Unknown state'
    
        self.logger.debug("Tv state["+self.status+"]")
    
    def get_current_service_info(self):
        '''
        Check status of vu stb.
        '''
        result = urllib.request.urlopen(self.vu_status_cmd)
        res = result.read()
        jres = json.loads(res)
        self.standby = jres['inStandby']
        self.channel = jres['currservice_station']
        self.program = jres['currservice_name']
        self.program_begin = jres['currservice_begin']
        self.program_end = jres['currservice_end']
        self.program_desc = jres['currservice_description']

    def reset_service_info(self):
        '''
        Reset info from Vu when tv activity is off 
        '''
        self.standby = "-"
        self.channel = "-"
        self.program = "-"
        self.program_begin = "-"
        self.program_end = "-"
        self.program_desc = "-"

    def get_announcement(self):
        '''
        Compile and return announcment.
        @return html encoded result
        '''
        return "Tv status " + self.status
    
if __name__ == '__main__':
    import davan.config.config_creator as configuration
    from davan.util import application_logger as log_manager
    
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = TvService("", config)
    test.enable(True)
 #   test.get_html_gui("0")
 