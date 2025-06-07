# -*- coding: utf-8 -*-
'''
@author: davandev
'''

import logging
import os
import urllib.request, urllib.parse, urllib.error
import json

from davan.http.service.base_service import BaseService
import davan.util.constants as constants
import davan.util.helper_functions as helper_functions

class NextBus():
    def __init__(self, arrives, area_name, timetable):
        self.arrive_in_minutes = arrives
        self.area_name = area_name
        self.timetable = timetable
        
    def toString(self):
        return "Arrives["+self.arrive_in_minutes+"] " \
               "Place["+self.area_name+"] "  \
               "TimeTable["+self.timetable+"]"
        
class DepartureService(BaseService):
    '''
    '''
    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.DEPARTURE_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.buses = []
        self.url = self.create_url()
        self.area_name_map = {'51425':'skyttens väg', '51424':'zenitvägen'}
        
    def create_url(self):
        url = "http://api.sl.se/api2/realtimedeparturesV4.json?key="
        url +=  self.config['DEPARTURE_SETTING']['REALTID']
        url += "&timewindow=30&siteid="
        url +=  self.config['DEPARTURE_SETTING']['SITEID']
        self.logger.debug("URL[" + url + "]")
        return url

    def parse_time_table(self, timetables, stop_area_number):
        '''
        Parse timetable
        '''
        self.logger.info("Parse stop:"+stop_area_number)
        buses = []
        for bus in timetables:
            self.logger.debug("Bus:" + str(bus))
            if str(bus['StopAreaNumber']) == stop_area_number:
                timetable=bus['TimeTabledDateTime']
                t=timetable.split('T', 1)[-1]
                t=t.rsplit(':', 1)[0]
                buses.insert(len(buses), NextBus(str(bus['DisplayTime']),
                                          bus['StopAreaName'],
                                          t))
        return buses

    def parse_request(self,msg):
        '''
        Determine if the request is for v-by or b-by
        @param msg
        '''
        if 'vby' in msg:
            return '51424','zenitvägen'
        else: # 'bby' in msg:
            return '51425','skyttens väg'
        
    def handle_request(self, msg):
        '''
        Received message from android device 
        '''
        self.logger.info("Received request for bus departure")

        sorted_timetable = []
        stop_id, stop_name = self.parse_request(msg)
        self.increment_invoked()

        result = urllib.request.urlopen(self.url)
        res = result.read()

        data = json.loads(res)

        for key, value in data.items():
            if key == "ResponseData":
                for k, v in value.items():
                    if k == "Buses":
                        sorted_timetable = self.parse_time_table(v, stop_id)

        msg = self.create_message(sorted_timetable,stop_name)
        
        self.services.get_service(constants.TTS_SERVICE_NAME).start(msg,constants.SPEAKER_HALLWAY)
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")
    
    def create_message(self, timetable, bus_stop_name):
        '''
        Compose the tts message 
        '''
        self.logger.info("Create tts message")
        msg = "Nästa buss från hållplats "+bus_stop_name+" går " + str(timetable[0].timetable) +"."
        if 'min' in timetable[0].arrive_in_minutes:
            msg +="Om " +timetable[0].arrive_in_minutes.replace('min',"minuter.")
        msg += "Därefter "
        
        for departure in timetable[1:]:
            msg +=  str(departure.timetable) + ", "
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
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
#         htmlresult = "Previous: " + str(self.previous_measure)+"\n"
#         htmlresult += "Last: " +str(self.last_measure)                
        htmlresult=""
        column  = column.replace("<SERVICE_VALUE>", htmlresult)

        return column
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config
    import davan.config.config_creator as configuration

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = DepartureService("",config)
    test.handle_request("msg")
