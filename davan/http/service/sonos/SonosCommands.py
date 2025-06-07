'''
Created on Sep 12, 2017

@author: davan
'''

import requests
import logging
import os

global logger
logger = logging.getLogger(os.path.basename(__file__))

ZONGROUPSTATE ="""<?xml version="1.0" ?><s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:GetZoneGroupState xmlns:u="urn:schemas-upnp-org:service:ZoneGroupTopology:1"/></s:Body></s:Envelope>"""

URL_ZONEGROUP = "/ZoneGroupTopology/Control"

headers = {'content-type': 'text/xml;charset="utf-8"'}

def get_zone_group_state(speaker_address, msg):
    logger.info("get zone group state")
    url = speaker_address + URL_ZONEGROUP
    headers = {'content-type': 'text/xml;charset="utf-8"','Soapaction':'"urn:schemas-upnp-org:service:ZoneGroupTopology:1#GetZoneGroupState"'}
    send_command(url, ZONGROUPSTATE, headers)

def send_command(url, body, headers):
    r = requests.post(url,data=body,headers=headers)
    logger.info("Status code:" + str(r.status_code))
    logger.info("Result:" + str(r.text))
