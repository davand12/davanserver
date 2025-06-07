# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import logging
import os
import urllib.request, urllib.parse, urllib.error
import time

import davan.config.config_creator as configuration
from davan.http.service.base_service import BaseService
import davan.util.constants as constants

class LogReceiverService(BaseService):
    '''
    Service receiving log messages from HC2 and writes to a log file
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,"LogEntry", service_provider, config)

        self.logger = logging.getLogger(os.path.basename(__file__))
        self.ok_rsp = 200
        
    
    def _parse_request(self,msg):
        self.logger.debug("Parse request:" + msg)
        msg = msg.replace("/LogEntry?text=", "")
        return urllib.parse.unquote(msg)
                
    def handle_request(self, msg):
        '''
        Received logentry from HC2, write to file.
        '''
        self.increment_invoked()
        if not os.path.exists(self.config['HC2LOG_PATH']):
            os.mkdir(self.config['HC2LOG_PATH'])
        
        logfile = self.config['HC2LOG_PATH'] + '/' + time.strftime("%Y-%m-%d", time.localtime()) + '.log'

        self.logger.debug("Received LogEntry ["+ msg + "] write to " + logfile)
        writemode = "w"
        if os.path.exists(logfile):
            writemode = "a"
        log_entry = self._parse_request(msg)
        fd = open(logfile,writemode)
        fd.write(log_entry + "\n")

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")

        
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = LogReceiverService()
    test.start("/authenticate?action=armSkalskydd")
