# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import logging
import os
import json
import re
import time
import traceback
import davan.util.helper_functions as helper 

import davan.config.config_creator as configuration
import davan.util.cmd_executor as cmd
import davan.util.constants as constants
from davan.http.service.speedtest.db_handle import DatabaseHandle
from davan.http.service.reoccuring_base_service import ReoccuringBaseService

class SpeedtestService(ReoccuringBaseService):
    '''
    Starts a re-occuring service that will measure internet speed (Download/Upload/ping)
    Requires speedtest-cli : installed with "sudo pip3 install speedtest-cli"
    wget https://install.speedtest.net/app/cli/ookla-speedtest-1.0.0-arm-linux.tgz
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.SPEEDTEST_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.command = cur_dir + os.sep+"./speedtest --progress=no --format=json"

        self.measure_time = ""
        self.ping = "-"
        self.download = "-"
        self.upload = "-"
        self.time_to_next_timeout = 900
        self.db = DatabaseHandle(config)

    def init_service(self):
        '''
        Create db table if not already present
        '''
        self.db.init_db()

    def handle_request(self, msg):
        '''
        Received request for the latest speedtest measurements.
        '''
        self.logger.info("Manual invoked SpeedTest")
        self.increment_invoked()
        self.handle_timeout()
        self.db.insert(self.upload,self.download,self.ping)

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")

    def calculate_speed(self, measure):
        '''
        Calculate the internet speed in Mbps
        '''
        downloaded_bytes = measure['bytes']
        elapsed = measure['elapsed']
        Mbits = 8/1000
        return int(Mbits*downloaded_bytes/elapsed)

    def update_virtual_device(self, item, value):
        '''
        Send current statistics to fibaro
        @param item, name of the fibaro field
        @param value, value to update
        '''
        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_SPEEDTEST'],
                                self.config['FIBARO_VD_SPEEDTEST_MAPPINGS'][item],
                                value)
        helper.send_auth_request(url,self.config)

    def handle_timeout(self):
        '''
        Timeout, time to measure speed
        '''
        self.logger.debug("Measure internet speed")
        self.measure_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        self.ping = "0"
        self.download = "0"
        self.upload = "0"
        
        try:
            result = str(cmd.execute_block(self.command, "speedtest", True))
            data = json.loads(result)
            self.ping = str(data['ping']['latency'])
            self.ping = self.ping.replace(".",",")

            self.download = str(self.calculate_speed(data['download']))
            self.upload = str(self.calculate_speed(data['upload']))

            self.db.insert(self.upload,self.download,self.ping)

            self.update_virtual_device("Time",self.measure_time)
            self.update_virtual_device("Upload",self.upload + " Mbps")
            self.update_virtual_device("Download",self.download+ " Mbps")
            self.update_virtual_device("Ping",self.ping+ " ms")
            self.update_virtual_device("Status","Ping[ "+self.ping+" ] DL[ "+self.download+" ] UL[ "+self.upload+" ]")
        except:
            self.logger.error("Received data["+result+"]")
            self.logger.error(traceback.format_exc())
            self.logger.warning("Caught exception when fetching internet speed")

    def get_announcement(self):
        '''
        Compile announcement to be read 
        '''
        announcement = "Senaste mätningen gjordes " + self.measure_time + ". "
        announcement += "Ping var " + self.ping + " millisekunder. "       
        announcement += "Nedladdningshastigheten var " + self.download + " megabit per sekund. "       
        announcement += "Uppladdningshastigheten var " + self.upload + " megabit per sekund. "       
        return announcement

    def get_next_timeout(self):
        '''
        Return time to next speed measuring
        '''
        return self.time_to_next_timeout
        
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
        htmlresult = "Ping: " + self.ping + " ms</br>\n"
        htmlresult += "Download: " + self.download + " Mbit</br>\n"
        htmlresult += "Upload: " + self.upload + " Mbit</br>\n"
        htmlresult += "Date: " + self.measure_time + " </br>\n"
        
        column = column.replace("<SERVICE_VALUE>", htmlresult)
        
        return column

if __name__ == '__main__':
    from davan.util import application_logger as app_logger
    config = configuration.create()
    
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = SpeedtestService("",config)
    test.handle_timeout()        