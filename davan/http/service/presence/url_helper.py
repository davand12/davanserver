'''
Created on 14 feb. 2016

@author: davandev
'''

import logging 
import os

global logger
logger = logging.getLogger(os.path.basename(__file__))

def getUserHomeUrl(config, user):
    '''
    Return the url to the fibaro scene to activate the user presence
    '''
    home_url = ""
    if user == "Mia":
        home_url = config["START_SCENE_URL"].replace("<ID>", config['MIA_HOME_SCENE_ID'])
    if user == "David":
        home_url = config["START_SCENE_URL"].replace("<ID>", config['DAVID_HOME_SCENE_ID'])
    if user == "Viggo":
        home_url = config["START_SCENE_URL"].replace("<ID>", config['VIGGO_HOME_SCENE_ID'])
    if user == "Wilma":
        home_url = config["START_SCENE_URL"].replace("<ID>", config['WILMA_HOME_SCENE_ID'])
    
    logger.debug("Url: ["+ home_url + "]")
    return home_url
    
def getUserAwayUrl(config, user):
    '''
    Return the url to the fibaro scene to deactivate the user presence
    '''
    away_url = ""
    if user == "mia":
        away_url = config["START_SCENE_URL"].replace("<ID>", config['MIA_AWAY_SCENE_ID'])
    if user == "david":
        away_url = config["START_SCENE_URL"].replace("<ID>", config['DAVID_AWAY_SCENE_ID'])
    if user == "viggo":
        away_url = config["START_SCENE_URL"].replace("<ID>", config['VIGGO_AWAY_SCENE_ID'])
    if user == "wilma":
        away_url = config["START_SCENE_URL"].replace("<ID>", config['WILMA_AWAY_SCENE_ID'])
    
    logger.debug("Url: ["+ away_url + "]")
    return away_url
