#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os
import logging
import urllib.request, urllib.parse, urllib.error
from urllib.parse import quote

global logger
logger = logging.getLogger(os.path.basename(__file__))

def debug_big(message):
    tmpStr = "\n==============================================================================\n"
    tmpStr += message + "\n"
    tmpStr += "==============================================================================\n"
    logger.info(tmpStr)

def debug_formated(obj):
    if isinstance(obj, dict):
        tmpStr = "\n==============================================================================\n"
        for k, v in sorted(obj.items()):
            tmpStr += '{0:30} ==> {1:15}'.format(str(k), str(v)) + str("\n")
        tmpStr += "\n==============================================================================\n"
        logger.debug(tmpStr)

    # List or tuple
    elif isinstance(obj, list) or isinstance(obj, tuple):
        for x in obj:
            logger.debug(x)

    # Other
    else:
        print(obj)
        
def createFibaroUrl(baseurl, vd_id, labelId, value):
    '''
    Create url to update virtual device on fibaro system 
    @param baseurl, base url to fibaro system
    @param vd_id, virtual device id
    @param labelId, label id of virtual device 
    @param value, value to set.
    '''
    baseurl = baseurl.replace('<DEVICEID>', vd_id)
    baseurl = baseurl.replace('<LABELID>', labelId)
    tempValue = quote(value, safe='') 
    baseurl = baseurl.replace('<VALUE>', tempValue)
    return baseurl

def create_fibaro_url_set_device_value(baseurl, vd_id, value):
    '''
    Create url to update virtual device on fibaro system 
    @param baseurl, base url to fibaro system
    @param vd_id, virtual device id
    @param labelId, label id of virtual device 
    @param value, value to set.
    '''
    baseurl = baseurl.replace('<ID>', vd_id)
    tempValue = quote(value, safe='') 
    baseurl = baseurl.replace('<VALUE>', tempValue)
    return baseurl

def create_fibaro_url_press_button(baseurl, vd_id, button_id):
    baseurl = baseurl.replace("<ID>", vd_id)
    baseurl = baseurl.replace("<BUTTONID>", str(button_id))
    return baseurl    

def send_telegram_message(config, msg):
    '''
    Send telegram message to all configured receivers
    @param msg message to send
    '''
    #logger.info("Sending telegram msg[ " + msg + "]")
    for chatid in config['CHATID']:
        url = config['TELEGRAM_PATH'].replace('<CHATID>', chatid) + urllib.parse.quote_plus(msg)
        #logger.info("Sending telegram : "+ url )
        urllib.request.urlopen(url)

def encode_message(message,encode_whitespace=True):
    '''
    Encode the quote
    '''
    
    message = str(message)
    if encode_whitespace:
        message = message.replace(" ","%20") 
    
    message = message.replace('ä','%C3%A4') 
    message = message.replace('å','%C3%A5') 
    message = message.replace('ö','%C3%B6') 
    message = message.replace('Ä','%C3%A4') 
    message = message.replace('Å','%C3%A5') 
    message = message.replace('Ö','%C3%B6') 

    message = message.replace('&auml;','%C3%A4')        
    message = message.replace('&aring;','%C3%A5')
    message = message.replace('&ouml;','%C3%B6') # ö
    #message = message.replace('&ouml;','%C3%B6')   
        
    logger.debug("Encoded message:" + message)
    return message

def decode_message(message,):
    '''
    Encode the quote
    '''
    logger.debug("Decoding message")
    message = str(message)
    message = message.replace('&auml;','ä')        
    message = message.replace('&aring;','å')
    message = message.replace('&ouml;','ö') # ö
    #message = message.replace('&ouml;','%C3%B6')   
        
    logger.debug("Encoded message:" + message)
    return message

def send_auth_request(url, config):
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, config['FIBARO_USER_NAME'], config['FIBARO_PASSWORD'])
    auth_handler = urllib.request.HTTPBasicAuthHandler(passman)
    opener = urllib.request.build_opener(auth_handler)
    urllib.request.install_opener(opener)            
    return urllib.request.urlopen(url)                
