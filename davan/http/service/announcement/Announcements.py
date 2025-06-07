#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
@author: davandev
'''
import os
import logging
import json
import traceback
import urllib.request, urllib.error, urllib.parse

import davan.util.application_logger as app_logger
import davan.config.config_creator as config_creator
import davan.util.helper_functions as helper_functions
from davan.util import constants

from datetime import datetime, timedelta
from datetime import *
from astral import Astral

global logger
logger = logging.getLogger(os.path.basename(__file__))

global weekdays
weekdays=['måndag','tisdag','onsdag','torsdag','fredag','lördag','söndag',]
months=['december','januari','februari','mars','april','maj','juni','juli','augusti','september','oktober','november','december']
date= ['noll','första','andra','tredje','fjärde','femte','sjätte','sjunde','åttonde','nionde','tionde',
       'elfte','tolfte','trettonde','fjortonde','femtonde','sextonde','sjuttonde','artonde','nittonde','tjugonde',
       'tjugoförsta','tjugoandra','tjugotredje','tjugofjärde','tjugofemte','tjugosjätte','tjugosjunde',
       'tjugoåttonde','tjugonionde','trettionde','trettiförsta']

def create_morning_announcement():
    n = datetime.now()
    t = n.timetuple()
    y, m, d, h, min, sec, wd, yd, i = t
    current_day = wd
    logger.debug("Current month [" + str(m) + "] Day [" + str(d) + ']')
    
    logger.info("Create morning announcement")
    announcement = "God morgon familjen äntligen är det en ny dag. Idag är det "
    announcement += str(weekdays[current_day]) + ' den '
    announcement += date[d] + " " + str(months[m]) + '. '
    
    return announcement

def create_afternoon_announcement():
    logger.info("Create afternoon announcement")
    announcement = "Halloj där, hoppas dagen varit bra. "
    return announcement

def create_night_announcement(name):
    '''
    '''
    logger.info("Create night announcement")
    announcement = name + " nu är det dags att gå och lägga sig. God natt och sov gott"
    
    return announcement
    
def create_water_announcement():
    '''
    
    '''
    logger.info("Create water announcement")
    announcement = "Kom ihåg att vattna blommorna och häcken"
    
    return announcement

def create_dead_in_covid_announcement():
    announcement = ""
    try:
        request = urllib.request.Request(
            "https://services5.arcgis.com/fsYDFeRKu1hELJJs/arcgis/rest/services/FOHM_Covid_19_FME_1/FeatureServer/3/query?f=geojson&where=1%3D1&outFields=*", 
            headers=constants.USER_AGENT_HEADERS)
        res = urllib.request.urlopen(request).read()
        data = json.loads(res)
        logger.debug("Res:" + str(data))

        features = data['features']
        dead = 0
        for feature in features:
            try:
                dead += int(feature['properties']['Totalt_antal_avlidna'])
            except:
                logger.error(traceback.format_exc())
        announcement = "Antalet avlidna i covid i Sverige är nu uppe i " + str(dead) + " stycken"
        
    except:
        logger.error(traceback.format_exc())
    return announcement

def create_sunset_sunrise_announcement():
    announcement = ""
    try:
        city_name = 'Stockholm'
        a = Astral()
        a.solar_depression = 'civil'
        city = a[city_name]
        sun = city.sun(date=datetime.now(), local=True)
    
        announcement = "Solens upp och nedgång idag."
    
        dawn = get_hour_and_minute(str(sun['dawn']))
        announcement += "Gryning klockan " + dawn + "."
    
        sunrise = get_hour_and_minute(str(sun['sunrise']))
        announcement += "Soluppgång klockan " + sunrise + "."
        
        sunset = get_hour_and_minute(str(sun['sunset']))
        announcement += "Solnedgång klockan " + sunset + "."
        
        dusk = get_hour_and_minute(str(sun['dusk']))
        announcement += "Skymning klockan " + dusk + "."
    except:
        logger.error(traceback.format_exc())
    return announcement

def get_hour_and_minute(dateitem):    
    dateitem = dateitem.split(" ")[1]
    dateitem= dateitem.split(":")
    return dateitem[0] +":" + dateitem[1]
    
def create_name_announcement():
    logger.info("Create name announcement")
    announcement = ""
    try:
        announcement = "Dagens namnsdagsbarn "
        
        request = urllib.request.Request("https://www.dagensnamn.nu/", headers=constants.USER_AGENT_HEADERS)
        encoded_result = str(urllib.request.urlopen(request).read())
        start_index = encoded_result.index("</span></div><h1>")
        start_index += 17
        stop_index = encoded_result.index("</h1><div class=")
        nr_of_char = stop_index-start_index 
        announcement += encoded_result[start_index:(start_index+nr_of_char)]
    
    except:
        logger.error(traceback.format_exc())
        logger.error("Failed to parse page: "+ str(encoded_result))
        
    return announcement + "."
    
def create_menu_announcement(config):
    '''
    Create menu announcement, a text file contains all daily menus
    Determine current date and read date from menu file.
    '''
    logger.debug("Create menu announcement")
    menu = ""
    try:
        n = datetime.now()
        t = n.timetuple()
        y, m, d, h, min, sec, wd, yd, i = t
        
        if wd >=5:
            logger.info("Weekend no menu")
            return ""
    
        todays_date = str(d) + "/" + str(m)
        logger.debug("today:" + todays_date)
        with open(config['ANNOUNCEMENT_MENU_PATH']) as f:
            content = f.readlines()
            for line in content:
                if line.startswith(todays_date):
                    logger.debug("Found todays menu: " + todays_date +": " + line)
                    menu = "Meny i Björkebyskolan. "
                    menu += line.replace(todays_date, "")
                    menu = menu.rstrip()
                    menu += "."
    except:
        logger.error(traceback.format_exc())

    return menu

def create_random_idiom(config):
    '''
    '''
    import random
    logger.debug("Create idiom announcement")
    menu = ""
    try:
        file_name = config['ANNOUNCEMENT_IDIOM']
        line_number, idiom = get_random_text_string(file_name)
        logger.debug("Found an idom: " + idiom )
        menu = "Dagens idiom. "
        menu += idiom
        menu = menu.rstrip()
        menu += " "
        update_file(file_name,line_number)
    except:
        logger.error(traceback.format_exc())

    return menu

def create_random_fact(config):
    '''
    '''
    import random
    logger.debug("Create fact announcement")
    menu = ""
    try:
        file_name = config['ANNOUNCEMENT_FACT']
        line_number, text = get_random_text_string(file_name)
        logger.debug("Found text: " + text )
        menu = "Dagens fakta. "
        menu += text
        menu = menu.rstrip()
        menu += " "
        update_file(file_name,line_number)
    except:
        logger.error(traceback.format_exc())

    return menu

def update_file(file_name, line):
    logger.debug("Update announcement file["+file_name+"]")
    with open(file_name, 'r') as file_handler:
        contents= file_handler.readlines()

        contents[line] = '--' + contents[line]

    with open(file_name, 'w') as file_handler:
        file_handler.writelines(contents)
        
def get_random_text_string(file_name):
    logger.debug("Get a random text string from " + file_name)
    import random
    with open( file_name ) as f:
        unique_text_found = False
        content = f.readlines()

        while not unique_text_found:
            line = random.randint(1, len(content))  
            if not content[line].startswith('--'):
                unique_text_found = True

        return line, content[line]
                
def create_theme_day_announcement(config):
    '''
    Create theme day announcement, a text file contains all daily themes
    Determine current date and read date from menu file.
    '''
    logger.debug("Create theme day announcement")
    result = ""
    try:
        n = datetime.now()
        t = n.timetuple()
        y, m, d, h, min, sec, wd, yd, i = t
        
        todays_date = str(d) + "/" + str(m)
        logger.debug("today:" + todays_date)
        with open(config['ANNOUNCEMENT_THEMEDAY_PATH']) as f:
            content = f.readlines()
            for line in content:
                if line.startswith(todays_date):
                    logger.debug("Found theme days: " + todays_date +": " + line)
                    result = "Tema idag, "
                    result += line.replace(todays_date, "")
                    result = result.rstrip()
                    result += "."
    except:
        logger.error(traceback.format_exc())

    return result
                
if __name__ == '__main__':
    config = config_creator.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    result = create_random_idiom(config)
    logger.info("Morning : "+ result)
    