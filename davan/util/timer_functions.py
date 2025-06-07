
'''
Created on 1 maj 2017

@author: davandev
'''
import time

import datetime
import calendar
from datetime import date
#from datetime import *
import logging
import os
from random import randint
import traceback

global logger
logger = logging.getLogger(os.path.basename(__file__))

def calculate_next_timeout(event_time):
    '''
    Calculate the number of seconds until the time expires
    @param event_time, expire time
    '''
    try:
        logger.debug("Calculate next timeout")
 #       current_time, _,_ = get_time_and_day_and_date()
        current_time = datetime.datetime.now().strftime('%H:%M')

#        logger.debug("Calculate next timeout:"+current_time)
        start_dt = datetime.datetime.strptime(current_time, '%H:%M')
        end_dt = datetime.datetime.strptime(event_time, '%H:%M')
        diff = (end_dt - start_dt) 
        if diff.days < 0:
            logger.warning("End is before start, fix it")
            # Set timeout to occur in 30 seconds 
            return 30 
    
        return diff.seconds
    except Exception:
        logger.error(traceback.format_exc())
        
def calculate_time_until_midnight():   
    '''
    When all events are executed, calculate time until midnight
    '''

    tomorrow = date.today() + datetime.timedelta(1)
    midnight = datetime.datetime.combine(tomorrow, datetime.time())
    now = datetime.datetime.now()
    time_to_next_event = (midnight - now).seconds + 60
    logger.debug("Sleep until midnight " + str(time_to_next_event) + " seconds")
    return time_to_next_event

def add_random_time(configured_time, randomValue):
    '''
    Adds a random value to the configured time.
    @param configured_time, configured expire time
    @param randomValue, the configured random value
    @return new expire time
    '''
    try:
        if randomValue == 0:
            return configured_time
        
        random = (randint(-randomValue,randomValue))
    
        start_dt = datetime.datetime.strptime(configured_time, '%H:%M')
        sum = (start_dt + datetime.timedelta(minutes=random)) 
        timeout = format(sum, '%H:%M')
        if "00:" in str(timeout):
            logger.warning("Timer expires after midnight, use original value")
            timeout = configured_time
        #logger.debug("Configured["+str(configured_time)+"] random["+str(random)+"] NewValue["+ str(timeout)+"]")
    
        return timeout
    except Exception:
        logger.error(traceback.format_exc())


def enabled_this_day(current_day, current_date, configured_interval):
    '''
    Check if this day is within the configured interval
    @return true if day is within interval false otherwise
    '''
    #logger.info("current_date="+str(current_date)+" Current day:"+str(current_day)+" configured_interval:["+str(configured_interval)+"]")
    if (current_day < 5 and configured_interval == "weekdays"):
        return True
    elif current_day >= 5 and current_day <=6 and configured_interval =="weekend":
        return True
    elif configured_interval == "week": 
        return True
    elif current_date == configured_interval:# example 15/2
        return True
    elif get_currrent_day_name() == configured_interval: # example Tuesday
        return True
    return False


def get_time_and_day_and_date():
    '''
    get current_day and current_time
    '''
    n = datetime.datetime.now()
    current_time = format(n,"%H:%M")
    current_date = format(n,"%d/%m")
    t = n.timetuple()
    y, m, d, h, min, sec, wd, yd, i = t
    current_day = wd
    #logger.debug("Day["+str(wd)+"]" + " Time["+str(current_time)+"] Date["+current_date+"]")
    return current_time, current_day, current_date

def get_currrent_day_name():
    n = datetime.datetime.now()
    return calendar.day_name[n.weekday()]
    
def get_seconds_to_next_hour():
    delta = datetime.timedelta(hours=1)
    now = datetime.datetime.now()
    next_hour = (now + delta).replace(microsecond=0, second=0, minute=2)

    wait_seconds = (next_hour - now).seconds  
    return wait_seconds

def get_time( wait_in_seconds):
    delta = datetime.timedelta(seconds=wait_in_seconds)
    now = datetime.datetime.now()
    sum = (now + delta) 
    return format(sum, '%H:%M')
