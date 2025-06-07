'''
@author: davandev
'''

import logging
import os
import traceback
import sys
import urllib.request, urllib.parse, urllib.error
import json
import davan.util.helper_functions as helper 
import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.util import cmd_executor as cmd_executor
from davan.http.service.base_service import BaseService


class UpsService(BaseService):
    ''' 
    classdocs
    service apcupsd restart

    Called from /etc/apcupsd/apccontrol when on battery with 
    script /etc/apcupsd/onbattery or /offbattery:
    #!/bin/sh
    #
    # This shell script if placed in /etc/apcupsd
    # will be called by /etc/apcupsd/apccontrol when the UPS
    # goes on batteries.
    # We send an email message to root to notify him.
    #
    curl http://192.168.2.44:8080/Ups?text=BatteryMode
    exit 0

    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,constants.UPS_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))

        # Apc access command
        self.command = "apcaccess"
        self.payload = "/Ups?text="
                    
    def parse_request(self, msg):
        '''
        Parse received request to get interesting parts
        @param msg: received request 
        '''
        msg = msg.replace(self.payload, "")
        return msg
             
    def handle_request(self, msg):
        '''
        Invoked from UPS or Fibaro system.
        UPS invokes script when status of UPS changes
        Fibaro invokes script to refresh status
        '''
        try:
            self.logger.debug("Received: " + msg ) 
            self.increment_invoked()
            result =""
            service = self.parse_request(msg)
            
            if constants.UPS_BATTERY_MODE in service:
                helper.send_telegram_message(self.config, "Ingen ström i huset!")
                self._update_changed_status_on_fibaro()
        
            elif constants.UPS_POWER_MODE in service:
                helper.send_telegram_message(self.config, "Strömmen är tillbaka")
                self._update_changed_status_on_fibaro()

            if constants.UPS_STATUS_REQ in service:
                result = self._handle_status_request()
            
            return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, result.encode("utf-8")
  
        except:
            self.logger.info("Failed to carry out ups request")
            self.increment_errors()
            traceback.print_exc(sys.exc_info())
 
    def _update_changed_status_on_fibaro(self):
        """
        Status changed on UPS, to either battery mode or power mode.
        Update virtual device on Fibaro system.
        """
        self.logger.info("UPS status changed")
        # Build URL to Fibaro virtual device
        url = helper.create_fibaro_url_press_button(
            self.config["VD_PRESS_BUTTON_URL"], 
            self.config['UPS_VD_ID'], 
            self.config["UPS_BUTTON_ID"])

        self.logger.debug("URL:"+url)
            
        # Send HTTP request to notify status change
        helper.send_auth_request(url,self.config)

    def _handle_status_request(self):
        '''
        Fetch status from UPS, 
        @return result json formatted
        '''
        self.logger.debug("Ups status request")
        response = cmd_executor.execute_block(self.command, self.command, True)
        parsedResponse = response.rstrip().split('\n')
        self.logger.debug("Parsed:" +str(parsedResponse))
        jsonResult = "{"
        for line in parsedResponse:
            if "STATUS" in line:
                status = line.split(":")
                jsonResult += '"Status":"'+status[1].replace(" ","")+'",'
            if "LOADPCT" in line:
                load = line.split(":")
                loadRes = load[1].replace("Percent Load Capacity","%")
                jsonResult += '"Load":"'+loadRes.lstrip()+'",'
            if "BCHARGE" in line:
                battery = line.split(":")
                battery = battery[1].replace("Percent","%")
                jsonResult += '"Battery":"'+battery.lstrip()+'",'
            if "TIMELEFT" in line:
                time = line.split(":")
                jsonResult += '"Time":"'+time[1].lstrip()+'"'
        jsonResult += "}"
        self.logger.info("Result: "+ jsonResult)
        return jsonResult
    
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
            return BaseService.get_html_gui(self, column_id)
            
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        _, _, result = self.handle_request("Status")
        data = json.loads(result)
        htmlresult = "<li>Status: " + data["Status"] + "</li>\n"
        htmlresult += "<li>Load: " + data["Load"] + " </li>\n"
        htmlresult += "<li>Battery: " + data["Battery"] + " </li>\n"
        htmlresult += "<li>Time: " + data["Time"] + " </li>\n"
        column = column.replace("<SERVICE_VALUE>", htmlresult)
        return column
    
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    upspath = "/Ups?text=Status"
    test = UpsService(None, config)
    test._handle_status_request()
