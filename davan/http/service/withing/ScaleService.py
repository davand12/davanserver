# -*- coding: utf-8 -*-

'''
@author: davandev
'''
import logging
import os
from datetime import *
import traceback

from nokia import NokiaAuth, NokiaApi, NokiaCredentials

import davan.util.constants as constants
import davan.util.timer_functions as timer_functions
import davan.util.helper_functions as helper_functions
from davan.http.service.reoccuring_base_service import ReoccuringBaseService
from __main__ import traceback

class ScaleService(ReoccuringBaseService):
    '''
    classdocs
    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.SCALE_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))

        logging.getLogger('oauthlib.oauth1').setLevel(logging.CRITICAL)
        logging.getLogger('requests_oauthlib.oauth1_auth').setLevel(logging.CRITICAL)

        self.creds = NokiaCredentials()
        self.creds.access_token=self.config['ACCESS_TOKEN']
        self.creds.access_token_secret=self.config['ACCESS_TOKEN_SECRET']
        self.creds.consumer_key=self.config['CONSUMER_KEY']
        self.creds.consumer_secret=self.config['CONSUMER_SECRET']
        self.creds.user_id=self.config['NOKIA_USER_ID']
        self.last_measure = None
        self.previous_measure = None
        self.time_to_next_event = 3600
        
    def handle_timeout(self):
        '''
        Calculate sun movements 
        '''
        self.logger.debug("Fetch scale update")
        try:
            client = NokiaApi(self.creds)
            measures = client.get_measures(limit=1)
            self.logger.debug("Checked weight["+str(measures[0].weight)+"] kg")
            
            if self.last_measure == None:
                self.last_measure = measures[0].weight
                
            elif self.last_measure == measures[0].weight:
                self.logger.debug("No change")
                return
    
            elif float(measures[0].weight) > float(self.last_measure):
    
                msg = "David, din lilla gris, du har ingen karaktär"
                self.services.get_service(constants.TTS_SERVICE_NAME).start(msg,constants.SPEAKER_KITCHEN)
            
            elif  float(measures[0].weight) <= float(self.last_measure):
                msg = "David, bra jobbat, fortsätt så"
                self.services.get_service(constants.TTS_SERVICE_NAME).start(msg,constants.SPEAKER_KITCHEN)
    
            self.previous_measure = self.last_measure
            self.last_measure = measures[0].weight
        except:
            self.logger.error(traceback.format_exc())
        #for measure in measures:
        #    self.logger.info(str(measure.weight))
        #self.logger.info("Your last measured weight: %skg" % measures[0].weight)
        #self.logger.info("Your nxt last measured weight: %skg" % measures[1].weight)
        
    def get_next_timeout(self):
        '''
        Return time until next timeout, only once per day.
        '''
        return self.time_to_next_event
    
        self.time_to_next_event = timer_functions.calculate_next_timeout("07:00")
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
        htmlresult = "Previous: " + str(self.previous_measure)+"\n"
        htmlresult += "Last: " +str(self.last_measure)                

        column  = column.replace("<SERVICE_VALUE>", htmlresult)

        return column

    def get_announcement(self):
        '''
        Compile and return announcment.
        @return html encoded result
        '''
        try:
            if self.last_measure == None:
                announcement = "Ingen mätning är tillgänglig"

            measures = str(self.last_measure).split(".")
            self.logger.info("last:" +str(measures[0]) + " kg and " +str(measures[1]) + " gram" )
            announcement ="Senaste vägningen visade " + measures[0] + " kg och "+ measures[1] + " gram"  

            if self.last_measure > self.previous_measure:
                announcement += " Det är en uppgång jämfört med vägningen innan"
            elif self.last_measure < self.previous_measure:
                announcement += " Det är en nedgång jämfört med vägningen innan"
        except:
            self.logger.error(traceback.format_exc())

        return announcement