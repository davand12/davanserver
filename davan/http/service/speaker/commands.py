import logging
import requests
import time
import json
import os
global logger
logger = logging.getLogger(os.path.basename(__file__))


GET_STATE ="http://192.168.50.92/api/v1/getState"
STOP = "http://192.168.50.92/api/v1/commands/?cmd=stop"
START = "http://192.168.50.92/api/v1/commands/?cmd=play"
PAUSE = "http://192.168.50.92/api/v1/commands/?cmd=pause"
REPLACE_AND_PLAY = "http://192.168.50.92/api/v1/replaceAndPlay"
INCREASE_VOLUME = "http://192.168.50.92/api/v1/commands/?cmd=volume&volume=plus"
DECREASE_VOLUME = "http://192.168.50.92/api/v1/commands/?cmd=volume&volume=minus"

def create_play_list(file_name):
    '''
    Send command to play a locally stored file.
    '''
    logger.info('Play file '+ file_name)
    payload = {
       "item": {
        "uri": "music-library/INTERNAL/announcement.mp3",
        "service": "mpd",
        "title": "Announcement_tone",
        "artist": "DavanServer",
        "album": "",
        "type": "song",
        "tracknumber": 0,
        "duration": 5,
        "trackType": "mp3"
        },        
        "list": [
        {
        "uri": "music-library/INTERNAL/announcement.mp3",
        "service": "mpd",
        "title": "Announcement_tone",
        "artist": "DavanServer",
        "album": "",
        "type": "song",
        "tracknumber": 0,
        "duration": 5,
        "trackType": "mp3"
        },
        {
        "uri": "music-library/INTERNAL/" + file_name,
        "service": "mpd",
        "title": "Announcement",
        "artist": "DavanServer",
        "album": "",
        "type": "song",
        "tracknumber": 0,
        "duration": 180,
        "trackType": "mp3"
        }
        ],
        "index": 0
    }
    return payload

def create_play_list_and_restore(file_name, current_play):
    '''
    Send command to play a locally stored file.
    '''
    logger.info('Play file '+ file_name)
    payload = {
        "list": [
        {
        "uri": "music-library/INTERNAL/announcement.mp3",
        "service": "mpd",
        "title": "Announcement_tone",
        "artist": "DavanServer",
        "album": "",
        "type": "song",
        "tracknumber": 0,
        "duration": 5,
        "trackType": "mp3"
        },
        {
        "uri": "music-library/INTERNAL/" + file_name,
        "service": "mpd",
        "title": "Announcement",
        "artist": "DavanServer",
        "album": "",
        "type": "song",
        "tracknumber": 0,
        "duration": 180,
        "trackType": "mp3"
        },
        {
        "service": current_play['service'],
        "type": current_play['trackType'],
        "title": "",
        "uri": current_play['uri'],
        "albumart": "",
        }         
    ],
        "index": 0
    }
    logger.info(str(payload))
    return payload

def play_announcement(payload):
    resp = requests.post(REPLACE_AND_PLAY, json=payload)
    logger.info("Resp: " +str(resp))
    return resp

def play_radio(url):
    logger.info('Play radio '+ url)
    payload = {
    "service": "webradio",
    "type": "webradio",
    "title": "",
    "uri": url,
    "albumart": ""
    }
    resp = requests.post(REPLACE_AND_PLAY, json=payload)
    logger.info("Resp: " +str(resp))
    return resp

def state():
    resp = requests.get(GET_STATE)
    logger.info("Resp: " +str(resp))
    return resp

def pause():
    resp = requests.get(PAUSE)
    logger.info("Resp: " +str(resp))
    return resp

def stop():
    resp = requests.get(STOP)
    logger.info("Resp: " +str(resp))
    return resp

def play():
    resp = requests.get(START)
    logger.info("Resp: " +str(resp))
    return resp

def increase():
    resp = requests.get(INCREASE_VOLUME)
    logger.info("Resp: " +str(resp))
    return resp

def decrease():
    resp = requests.get(DECREASE_VOLUME)
    logger.info("Resp: " +str(resp))
    return resp
