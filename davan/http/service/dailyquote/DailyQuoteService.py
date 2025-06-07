# -*- coding: utf-8 -*-

'''
@author: davandev
'''
import logging
import os
import time
import urllib.request, urllib.error, urllib.parse
import traceback
import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.timer_functions as timer_functions
import davan.util.helper_functions as helper_functions
from davan.util import application_logger as app_logger
from davan.http.service.reoccuring_base_service import ReoccuringBaseService

class DailyQuoteService(ReoccuringBaseService):
    '''
    classdocs
    sys.setdefaultencoding('latin-1')

    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        kjz442
        '''
        ReoccuringBaseService.__init__(self, constants.QUOTE_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.quote_url = "http://www.dagenscitat.nu/citat.js"
        self.quote2_url = "http://www.knep.se/dagens/ordsprak.js"
        self.quest_url = "http://www.knep.se/dagens/gata.js"
        # Number of seconds until next event occur
        self.time_to_next_event = 25
        # Todays calendar events
        self.today_quote = None
        self.today_quest = None
        self.today_answer = None

    def do_self_test(self):
        try:
            quote = str(urllib.request.urlopen(self.quote_url).read())
            quote = quote.split(">")[1]
            self.today_quote = quote.split("<")[0]
            if(not self.today_quote):
                raise Exception("")
        except:
            self.logger.error(traceback.format_exc())

            self.logger.warning("Self test failed")
            msg = "Failed to fetch daily quote"
            self.raise_alarm(msg,"Warning",msg)

                       
    def handle_timeout(self):
        '''
        Fetch quote from dagenscitat.nu 
        '''
        self.logger.debug("Fetching quote")
        quote = str(urllib.request.urlopen(self.quote_url).read())
        quote = quote.split(">")[1]
        self.today_quote = quote.split("<")[0]
        self.today_quote = helper_functions.decode_message(self.today_quote)
        #self.get_quest()

    def get_quest(self):
        self.logger.debug("Fetching quest")
        quest = str(urllib.request.urlopen(self.quest_url).read())
        quest = quest.split(">\\")[1]
        answer = quest.split("</div>")[1]
        quest = quest.split("</div>")[0]
        quest = quest.replace('"','')
        self.today_quest = quest.replace('\\','')
        
        answer = answer.split('display:none')[1]
        answer = answer.split(">")[1]
        self.today_answer = answer.split("<")[0]        
        
    def get_next_timeout(self):
        '''
        Return time until next timeout, only once per day.
        '''
        if self.today_quote == None: # First time timeout after 30 s.
            return self.time_to_next_event
        
        self.time_to_next_event = timer_functions.calculate_time_until_midnight()
        self.logger.debug("Next timeout in " + str(self.time_to_next_event) +  " seconds")
        return self.time_to_next_event
        
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
        quote = str(self.today_quote) + "</br>\n"
        quote += str(self.today_quest) + "</br>\n"
        quote += str(self.today_answer) + "</br>\n"
        
        column  = column.replace("<SERVICE_VALUE>", quote)

        return column

    def get_announcement(self):
        '''
        Compile and return announcment.
        @return html encoded result
        '''
        result = ""
        if self.today_quote:
            result = "Dagens citat. "
            result += self.today_quote +"."
        
        return result

    def get_quest_announcement(self):
        '''
        Compile and return announcment.
        @return html encoded result
        '''
        result = "Dagens gåta. "
        result += self.today_quest
    
        return result

if __name__ == '__main__':
    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = DailyQuoteService("",config)
    test.get_quest()
