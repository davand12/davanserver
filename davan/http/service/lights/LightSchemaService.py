
'''
@author: davandev
'''

import logging
import os
import traceback
import urllib.request, urllib.parse, urllib.error

import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper 
import davan.util.timer_functions as timer_functions
import davan.util.fibaro_functions as fibaro_functions
from davan.http.service.reoccuring_base_service import ReoccuringBaseService
import datetime

class TimeEvent():
    def __init__(self, room, time, device_type, light_level ,device_id, label_id, virtual_device_id, onoff, enabled_when_armed):
            self.logger = logging.getLogger(os.path.basename(__file__))

            self.room = room.strip()
            self.time = time.strip()
            self.device_type = device_type.strip()
            self.light_level = light_level.strip()
            self.device_id = device_id.strip()
            self.label_id = label_id.strip()
            self.virtual_device_id = virtual_device_id.strip()
            self.onoff = onoff.strip()
            if enabled_when_armed == "1":
                self.enabled_when_armed = True
            else:
                self.enabled_when_armed = False
            

    def toString(self):
        return "Room[ "+self.room+" ] "\
            "VD[ "+self.virtual_device_id+" ] "\
            "Action[ "+self.onoff+" ] "\
            "DeviceId[ "+self.device_id+" ] "\
            "DeviceType[ "+self.device_type+" ] "\
            "DimmerValue[ "+self.light_level+" ] "\
            "ButtonId[ "+str(self.label_id)+" ] "\
            "Enabled_when_armed[ "+str(self.enabled_when_armed)+" ]"
        
class LightSchemaService(ReoccuringBaseService):
    '''
    Notice requires ntplib
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.LIGHTSCHEMA_SERVICE, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        # Sorted list of event to execute during the day
        self.todays_events = []
        # Current time  
        self.current_time = ""
        # Current weekday (0-6)
        self.current_day = -1
        # Number of seconds until next event occur
        self.time_to_next_event = -1
  
    def get_next_timeout(self):
        '''
        Return time to next timeout
        '''
        if self.time_to_next_event == -1: # First time, wait 15 sec to get sunset
            self.time_to_next_event = 0
            return 15
        
        if len(self.todays_events) > 0:
            self.time_to_next_event = timer_functions.calculate_next_timeout(self.todays_events[0].time)
            self.logger.debug("Next timeout " + self.todays_events[0].time + " in " + str(self.time_to_next_event) +  " seconds")
        else:
            self.detemine_todays_events()
    
        return self.time_to_next_event
    
    def handle_timeout(self):
        '''
        Timeout received, fetch event and perform action.
        '''
        self.logger.debug("Got a timeout, trigger light event")
        try:
            event = self.todays_events.pop(0)
            self.invoke_event(event)
                                
        except:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
    
    def invoke_event(self, event):
        '''
        Execute event
        @param event event to be executed
        '''
        if event.enabled_when_armed and not fibaro_functions.is_alarm_armed(self.config):
            self.logger.info("Event is only triggered when alarm is armed")
            return
            
        self.logger.info("Invoking event:" + event.toString())
        if event.device_type == "1" and event.onoff == "turnOn": # Lightlevel configured
            url = helper.create_fibaro_url_set_device_value(
                    self.config['DEVICE_SET_VALUE_WITH_ARG_URL'], 
                    event.device_id, 
                    event.light_level)
        elif event.device_type =="2": #Virtualdevice
            button_id = int(event.light_level)
            if event.onoff == "turnOff":
                button_id +=1
            url = helper.create_fibaro_url_press_button(
                    self.config['VD_PRESS_BUTTON_URL'],
                    event.device_id,
                    button_id)
        elif event.device_type =="3": # Notify Service
            self.logger.info("Invoking scheduled service " + event.room)
            service = self.services.get_service(event.room)
            service.handle_request(event.room + "?service=" + event.onoff )
            url = ""
        else: # Just on/off switch
            url = helper.create_fibaro_url_set_device_value(
                    self.config['DEVICE_SET_VALUE_URL'], 
                    event.device_id, 
                    event.onoff)
                
        message = "Light is turned on"
        if event.onoff == "turnOff":
            message = "Light is turned off"
        
        # update status label of virtual device    
        self.update_virtual_device(event.virtual_device_id, "6", message)
        self.logger.debug("URL:"+url)
        if url != "":
            urllib.request.urlopen(url)        
            
    def schedule_events(self):
        '''
        Schedule all configured events and update all virtual devices with
        the schedules.
        '''
        configuration = self.config['LIGHT_SCHEMA']
        for event in configuration:
            items = event.split(",")
            if not timer_functions.enabled_this_day(self.current_day,
                                                    self.current_time,
                                                    items[3].strip()):
                self.update_virtual_device(items[9].strip(),
                                       items[7].strip(),
                                       "")
                self.logger.debug("Event Timer ["+items[0].strip()+"] not configured this day")
                continue
            starttime = items[1].strip()
            if starttime == "sunset":
                starttime = self.services.get_service(constants.SUN_SERVICE_NAME).get_sunset()
                self.logger.debug("Sunset configured: " + str(starttime))
            elif starttime == "dusk":
                starttime = self.services.get_service(constants.SUN_SERVICE_NAME).get_dusk()
                self.logger.debug("Dusk configured: " + str(starttime))

            starttime = timer_functions.add_random_time(starttime,int(items[7].strip()))
            
            self.todays_events.append(TimeEvent(items[0].strip(),  # Room name
                                                starttime, # Start time
                                                items[4].strip(),  # Device type
                                                items[5].strip(),  # Light level
                                                items[6].strip(),  # Device id
                                                items[7].strip(),  # labelid
                                                items[9].strip(),  # virtualdevice id
                                                constants.TURN_ON,
                                                items[10].strip()))
            
            stoptime = timer_functions.add_random_time(items[2].strip(),int(items[7].strip()))
            self.todays_events.append(TimeEvent(items[0].strip(),
                                                stoptime,
                                                items[4].strip(),
                                                items[5].strip(),
                                                items[6].strip(),
                                                items[7].strip(), 
                                                items[9].strip(),
                                                constants.TURN_OFF,
                                                items[10].strip()))
            
            self.update_virtual_device(items[9].strip(),
                                       items[7].strip(),
                                       str(items[0].strip() +" "+starttime+ " => " + stoptime))
        
    def detemine_todays_events(self):
        '''
        run at midnight, calculates all events that should occur this day. 
        '''
        self.logger.debug("Weekday["+str(datetime.datetime.today().weekday())+"] current_day["+str(self.current_day)+"]")
        if(str(datetime.datetime.today().weekday()) != str(self.current_day)): # Check if new day
            self.current_time,self.current_day, _ = timer_functions.get_time_and_day_and_date()
            self.schedule_events()
            self.todays_events = self.sort_events(self.todays_events)
            if (len(self.todays_events) > 0):
                self.time_to_next_event = timer_functions.calculate_next_timeout(self.todays_events[0].time)
                self.logger.debug("Next timeout [" + self.todays_events[0].time + "] in " + str(self.time_to_next_event) +  " seconds")
            else:
                self.logger.debug("No events are configured, stop timer")
        else:
            self.time_to_next_event = timer_functions.calculate_time_until_midnight()
            #self._calculate_time_until_midnight()
            self.logger.info("No more timers scheduled, wait for next re-scheduling in "+ str(self.time_to_next_event) + " seconds")
  
    def sort_events(self, events):
        '''
        Sort all events based on when they expire. 
        Remove events where expire time is already passed.
        @param events list of all events
        '''
        future_events = []
        for event in self.todays_events:
            if (event.time > self.current_time):
                future_events.append(event)
            else:
                self.logger.info("Time ["+event.time+"] is already passed")
            
        sorted_events = sorted(future_events, key=lambda timeEvent: timeEvent.time)
        event_index = 0
        for event in sorted_events:
            self.logger.info("Event["+str(event_index)+"] " + str(event.time) + " " + str(event.room) + " " + str(event.onoff))
            event_index +=1
        return sorted_events
    
    def update_virtual_device(self, virtualdevice, labelid, message):
        '''
        Update virtual device on fibaro system with todays schedule
        @param virtualdevice virtual device id
        @param labelid label id on virtual device
        @param message message to display
        '''
        if virtualdevice != "-1":
            url = helper.createFibaroUrl(
                                self.config['UPDATE_DEVICE'], 
                                virtualdevice, 
                                self.config['LABEL_SCHEDULE'].replace("<BID>",labelid), 
                                message)
            self.logger.debug("URL:"+url)
            
            helper.send_auth_request(url,self.config)
                    
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
        htmlresult = ""
        if len(self.todays_events) >0:
            for event in self.todays_events:
                htmlresult += "<li>" + str(event.room) + " "+str(event.time)+" "+str(event.onoff)+"</li>\n"
        else:
                htmlresult += "<li>No more scheduled events today</li>\n"            
        column = column.replace("<SERVICE_VALUE>", htmlresult)

        return column        
            
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    service = LightSchemaService(config)
    service.alarm_is_armed()
    
