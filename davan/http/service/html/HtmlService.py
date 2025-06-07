# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import builtins
import logging
import os
import time
import re
import traceback

import davan.util.cmd_executor as cmd
import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.http.service.base_service import BaseService
from davan.util import application_logger as log_config

class HtmlService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.HTML_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        
        self.start_date = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        self.expression = re.compile('<(.*?)object')
   
    def handle_request(self, msg):
        '''
        Received html request.
        '''
        self.logger.debug("Received html request: [" + msg + "]")
        self.increment_invoked()

        if ("applicationserver.log" in msg):
            logfile = msg.replace(".html","")
            self.logger.info("Logfile: "+ self.config['LOGFILE_PATH'] + " File "+ logfile)
            f = open(self.config['LOGFILE_PATH'] + logfile) 
            content = f.read()
            content = content.replace("\n","<br>")
        elif (msg == "/index.html"):
            f = open(self.config["HTML_INDEX_FILE"])
            content = f.read()
            f.close()
            result = self.generate_service_fragment()
            content = content.replace("<SERVICES>", result)
            content = self.get_server_info(content)
        elif (msg == "/select_logfile.html"):
            f = open(self.config["HTML_SELECT_LOGFILE"])
            content = f.read()
            f.close()
        elif (msg == "/style.css"):
            f = open(self.config["HTML_STYLE_FILE"])
            content = f.read()
            f.close()
            return constants.RESPONSE_OK, constants.MIME_TYPE_CSS, content.encode("utf-8")

        elif (msg == "/logfiles.html"):
            content = self.get_logfiles()
        elif (msg == "/reboot.html"):
            content = "Server restarting"
        elif (msg == "/statistics.html"):
            content = self.get_statistics()
        elif (msg == "/status.html"):
            content = self.get_status()
           
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, content.encode("utf-8")
    
    def generate_service_fragment(self):
        '''
        Iterate all services, generate and return the services page 
        '''
        try:
            column_id = 1
            tot_result = ""
            for name, service in builtins.davan_services.services.items():
                try:
                    if column_id == 1:
                        tot_result += '<div id="columns">\n'
                            
                    tot_result += service.get_html_gui(column_id)
                    column_id += 1
                    if column_id == 4:
                        tot_result += '<div style="clear: both;"> </div></div>\n' 
                        column_id = 1
                except :
                    self.logger.error(traceback.format_exc())        
        
            tot_result += '<div style="clear: both;"> </div></div>\n' 
            return tot_result 
        except :
            self.logger.error(traceback.format_exc())        
    
    def get_logfiles(self):
        """
        Return the content of the current logfile
        """
        f = open(self.config['SERVICE_PATH'] + "html/log_file_template.html")
        content = f.read()
        f.close()

        options = ""
        for logfile in os.listdir(self.config["LOGFILE_PATH"]):
            if "applicationserver" in logfile:
                options +='<option value="http://192.168.2.50:8080/' + logfile + '.html">' + logfile + '</option>'
        content = content.replace("<OPTIONS_LOGFILES>", options)
        return content 
    
    def get_statistics(self):
        """
        Return statistics of running services
        """
        self.logger.info("Statistics")
        f = open(self.config["HTML_STATISTICS_FILE"])
        content = f.read()
        stat= constants.HTML_TABLE_START
        for key, value in builtins.davan_services.services.items():
            service = self.expression.findall(str(value))[0]
            service_name = service.split(".")[0]
            success, error = value.get_counters()
            stat += "<tr><th>" + str(service_name) + "</th><th>" + str(success) + "</th><th>" + str(error) + "</th></th>"  
        stat += constants.HTML_TABLE_END
        content = content.replace("<SERVICES_STATISTICS_VALUE>", stat)
        return content
    
    def get_server_info(self, content):
        '''
        Return information/statistics about server
        '''
        content = content.replace('<SERVER_STARTED_VALUE>', self.start_date)
        result = (cmd.execute_block("uptime", "uptime", True)).split()
        content = content.replace('<UPTIME>', str(result[2]) + " " + str(result[3]))
        content = content.replace('<CPU_VALUE>', str(result[9]))
        result = (cmd.execute_block("df -hl | grep root", "memory usage", True)).split()
        content = content.replace('<DISK_VALUE>', str(result[4]) + " ( Free " + str(result[3]) + " )")
        result = (cmd.execute_block("free -h  | grep Mem | awk '{print $3,$4}'", "memory usage", True)).split()
        content = content.replace('<RUNNING_SERVICES_VALUE>', str(len(list(builtins.davan_services.services.items())))) 
        return content
    
    def get_status(self):
        '''
        Return the status of the server.
        @return: status json formatted
        '''
        result = (cmd.execute_block("uptime", "uptime", True)).split()
        uptime = str(result[2]) + " " + str(result[3])
        cpuload = str(result[9])
        result = (cmd.execute_block("df -hl | grep root", "memory usage", True)).split()
        diskusage = str(result[4]) + " ( Free " + str(result[3]) + " )"
        result = (cmd.execute_block("free -h  | grep Mem | awk '{print $3,$4}'", "memory usage", True)).split()
        memory_used = str(result[0])
        memory_free = str(result[1])
        services = len(list(builtins.davan_services.services.keys()))
        json_string = '{"Uptime": "'+uptime+'", "ServerStarted":"'+str(self.start_date)+'","CpuLoad":"'+cpuload+'", "Disk":"'+diskusage+'", "Memory":"'+memory_used+'/'+memory_free+'",  "Services":"'+str(services)+'"}'
        return json_string
    