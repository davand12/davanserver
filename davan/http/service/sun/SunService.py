# -*- coding: utf-8 -*-

'''
@author: davandev
'''
import logging
import os
import traceback

from datetime import *
from astral import Astral

import davan.util.constants as constants
import davan.util.timer_functions as timer_functions
import davan.util.helper_functions as helper_functions
from davan.http.service.reoccuring_base_service import ReoccuringBaseService

class SunService(ReoccuringBaseService):
    '''
    classdocs
    sys.setdefaultencoding('latin-1')
    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.SUN_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.dawn =None
        self.rise =None
        self.dusk =None
        self.set=None
        
        self.time_to_next_event = 0

    def do_self_test(self):
        try:
            self.calculate_sun_movements()
        except:
            self.logger.error(traceback.format_exc())

            msg = "Self test failed"
            self.logger.error(msg)
            self.raise_alarm(msg,"Warning",msg)


    def handle_timeout(self):
        '''
        Calculate sun movements 
        '''
        try:
            self.calculate_sun_movements()
        except:
            self.logger.error(traceback.format_exc())
            self.increment_errors()

    def calculate_sun_movements(self):
        self.logger.debug("Calculating sun movements")
        city_name = 'Stockholm'
        a = Astral()
        a.solar_depression = 'civil'
        city = a[city_name]
        sun = city.sun(date=datetime.now(), local=True)
    
        self.dawn = self.get_hour_and_minute(str(sun['dawn']))
        self.rise = self.get_hour_and_minute(str(sun['sunrise']))
        self.set = self.get_hour_and_minute(str(sun['sunset']))
        self.dusk = self.get_hour_and_minute(str(sun['dusk']))

    def get_sunset(self):
        return self.set

    def get_dusk(self):
        return self.dusk
    
    def get_hour_and_minute(self, dateitem):    
        dateitem = dateitem.split(" ")[1]
        dateitem= dateitem.split(":")
        return dateitem[0] +":" + dateitem[1]

    def get_next_timeout(self):
        '''
        Return time until next timeout, only once per day.
        '''
        if self.set == None: # First time timeout after 30 s.
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
        quote = "Dawn: " + self.dawn +"</br>\n"
        quote += "Rise: " + self.rise +"</br>\n"
        quote += "Set: " + self.set +"</br>\n"
        quote += "Dusk: " + self.dusk +"</br>\n"  
        
        column  = column.replace("<SERVICE_VALUE>", quote)

        return column

    def get_announcement(self):
        '''
        Compile and return announcment.
        @return html encoded result
        '''
        announcement = "Solens upp och nedgång idag."
    
        announcement += "Gryning klockan " + self.dawn + "."
        announcement += "Soluppgång klockan " + self.rise + "."
        announcement += "Solnedgång klockan " + self.set + "."
        announcement += "Skymning klockan " + self.dusk + "."
        return announcement
    