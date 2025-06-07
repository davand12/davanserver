#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
@author: davandev
'''


import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import davan.util.helper_functions as helper_functions
import davan.util.timer_functions as timer_functions

import logging
from threading import Thread, Event
import datetime

import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.http.service.reoccuring_base_service import ReoccuringBaseService

class CalendarEvent():
    def __init__(self, calendar, event):
        self.calendar = calendar
        self.event = event

    def toString(self):
        return "calendar "+self.calendar+" "\
               "event "+self.event+" "

class CalendarService(ReoccuringBaseService):
    '''
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.CALENDAR_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        # Disable logging from googleapiclient.
        logging.getLogger('googleapiclient.discovery').setLevel(logging.CRITICAL)
        self.SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
        self.CLIENT_SECRET_FILE = self.config['GOOGLE_CALENDAR_TOKEN']#'/home/pi/client_secret.json'
        self.APPLICATION_NAME = 'CalendarService'
        # Number of seconds until next event occur
        self.time_to_next_event = 30
        # Todays calendar events
        self.todays_events = None
    
    def do_self_test(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http,cache_discovery=False)
        calendar_list =service.calendarList().list(pageToken=None).execute()
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] =='David':
                return

        self.logger.error("Self test failed")
        msg = "Failed to fetch calendar"
        self.raise_alarm(msg,"Warning",msg)


    def handle_timeout(self):
        '''
        Fetch todays calendar events
        '''
        self.logger.debug("Fetch todays calendar events")
        self.todays_events = []
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http,cache_discovery=False)
    
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        seconds_to_tomorrow = timer_functions.calculate_time_until_midnight() - 60
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds_to_tomorrow)
        tomorrow = tomorrow.isoformat() + 'Z'
        
        page_token = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                self.logger.debug("Calendar[" + calendar_list_entry['summary'] + "]")
                eventsResult = service.events().list(
                    calendarId=calendar_list_entry['id'], timeMin=now,timeMax=tomorrow,maxResults=10, singleEvents=True,
                    orderBy='startTime').execute()
                events = eventsResult.get('items', [])
                for today_event in events:
                    self.logger.info("Calendar[" + calendar_list_entry['summary'] + "] Event[" + today_event['summary'] + "]")
                    start = today_event['start'].get('dateTime', today_event['start'].get('date'))
                    event = CalendarEvent(calendar_list_entry['summary'],today_event['summary'])
                    self.todays_events.append(event)
                    #self.logger.info(event.toString())
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        if len(self.todays_events)== 0:
            self.logger.debug("No event today")

    def get_next_timeout(self):
        '''
        Return time until next timeout, only once per day.
        '''
        if self.todays_events == None: # First time timeout after 30 s.
            return self.time_to_next_event
        
        self.time_to_next_event = timer_functions.calculate_time_until_midnight()
        self.logger.debug("Next timeout in " + str(self.time_to_next_event) +  " seconds")
        return self.time_to_next_event
    
    def get_credentials(self):
        """
        Gets valid user credentials from storage.
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'calendar-python-quickstart.json')
    
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = constants.CALENDAR_SERVICE_NAME
            credentials = tools.run(flow, store)
        return credentials
    
    def get_announcement(self):
        '''
        Return todays events.
        '''
        if len(self.todays_events)== 0:
            self.logger.info("No event today")
            announcement = "Dagens schema. Ingen planerad aktivitet idag."
        else:
            announcement = "Dagens schema. "
            for calendar_event in self.todays_events:
                announcement += str(""+calendar_event.event)
                announcement += ". "
                #source = calendar_event.event.encode("utf-8")
                #announcement += source + ". "
        
        return announcement

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
        if self.todays_events != None and len(self.todays_events) >0:
            for event in self.todays_events:
                htmlresult += "<li>" 
                htmlresult += str(event.calendar.encode("utf-8")) 
                htmlresult += " " 
                htmlresult += str(event.event.encode("utf-8")) 
                htmlresult += "</li>\n"
                
        else:
            htmlresult += "<li>No more scheduled events today</li>\n"            
        
        htmlresult = helper_functions.encode_message(htmlresult,False)
        column = column.replace("<SERVICE_VALUE>", htmlresult)

        return column        
    
if __name__ == '__main__':
    from davan.util import application_logger as log_config
    import time
    
    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=3)
    
    test = CalendarService("", config)
    test.handle_timeout()
    test.stop_service()
