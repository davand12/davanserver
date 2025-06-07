'''





Robot Data:
{
  ver: '3',
  hostname: 'iRobot-E3513FD46E1A4EFEB4336ED260280551',
  robotname: 'Bogda',
  robotid: 'E3513FD46E1A4EFEB4336ED260280551',
  ip: '192.168.2.110',
  mac: '50:14:79:23:74:49',
  sw: 'lewis+3.14.16+lewis-release-121+21',
  sku: 'i715040',
  nc: 0,
  proto: 'mqtt',
  cap: {
    binFullDetect: 2,
    dockComm: 1,
    wDevLoc: 2,
    bleDevLoc: 1,
    edge: 0,
    maps: 3,
    pmaps: 5,
    tLine: 2,
    area: 1,
    eco: 1,
    multiPass: 2,
    pose: 1,
    team: 1,
    pp: 0,
    lang: 2,
    '5ghz': 1,
    prov: 3,
    sched: 1,
    svcConf: 1,
    ota: 2,
    log: 2,
    langOta: 0,
    tileScan: 1
  },
  blid: 'E3513FD46E1A4EFEB4336ED260280551'
}
Password=> :1:1625084722:9dXs2npZq134h4jZ <= Yes, all this string.
Use this credentials in dorita980 lib :)
'''

import logging
import os
import re
import traceback
from davan.http.service.base_service import BaseService
from davan.util import application_logger as app_logger
import davan.util.constants as constants
import davan.util.helper_functions as helper
import davan.config.config_creator as configuration
import requests
import time
import json
import davan.util.helper_functions as helper 
import davan.http.service.roomba.RoombaStateUtilities as StateUtil      
from davan.http.service.base_service import BaseService
from davan.http.service.roomba.RoombaHandle import RoombaHandle
from davan.http.service.roomba.RoombaHandle import ManualRun

import davan.http.service.roomba.RoombaCommands as RoombaCommands  
import asyncio
import davan.http.service.roomba.MqttClient as MqttClient 
import davan.util.cmd_executor as cmd_executor

class RoombaService(BaseService):
    '''
    Control roomba     
    Dependent on receiving MQTT data from
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.ROOMBA_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.user = config['ROOMBA_USER']
        self.pwd = config['ROOMBA_PWD']
        self.host = config['ROOMBA_HOST']
        
        self.handle = None
        self.cmd = None
        self.client = None 

    def _parse_request(self,msg):
        self.logger.info("Parse request:" + msg)
        msg = msg.replace("/RoombaService?", "")
        cmds = msg.split("=")
        return  cmds[0], cmds[1]

    def handle_request(self, msg):
        '''
        Received request to start cleaning a room from HC2.
        '''
        try:
           self.logger.info("Handle request :" + msg)
           roomname, action = self._parse_request(msg)
           self.handle.data.roomname = roomname
           self.handle.sm.change_state( ManualRun( self.handle.data ))
           message = RoombaCommands.build_cmd( roomname, self.config )
           self.logger.debug("Command:" + message )
           self.client.publish('/roomba/command/Bogda/',message)
           self.increment_invoked()
        except Exception as ex:
           self.logger.info("Caught exception " + str(ex))
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")


    def init_service(self):
        try:
           if not cmd_executor.execute_block('pgrep mosquitto',return_output=True):
               self.raise_alarm("Mosquitte not running","Error","Mosquitto not running") 
               self.logger.error("Mosquitto is NOT running")
           else:
               self.logger.info("Mosquitto is running")
           result = cmd_executor.execute_block('ps -ef |grep roomba_to_mqtt_generator.py |wc -l',return_output=True)
           if int(result)<2: 
               self.raise_alarm("Roomba mqtt subscriber not running","Error","Roomba mqtt subscriber not running") 
               self.logger.error("Roomba mqtt subscriber not running")
           else:
               self.logger.info("Roomba mqtt subscriber running")


           self.handle = RoombaHandle( self.config, self.services )
           self.client = MqttClient.MyMqttClient(self)
           self.client.start()

        except Exception as ex:
           self.logger.info("Caught exception " + str(ex))
             
    
    def message_received(self, message):
        try:
            self.handle.handle_data(message)
            StateUtil.notify( self.handle.data )
            self.report_status( self.handle.data )
        except Exception as ex:
           self.logger.info("Caught exception " + str(ex))

    def report_status(self, stateData):
        '''
        Send updates to fibaro virtual device
        '''
        
        if stateData.current_phase:
            url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROOMBA_ID'],
                                self.config['FIBARO_VD_ROOMBA_MAPPINGS']['State'],
                                StateUtil.states[stateData.current_phase])
            helper.send_auth_request(url,self.config)
        
        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROOMBA_ID'],
                                self.config['FIBARO_VD_ROOMBA_MAPPINGS']['Battery'],
                                stateData.batPct + " %")
        helper.send_auth_request(url,self.config)

        url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                self.config['FIBARO_VD_ROOMBA_ID'],
                                self.config['FIBARO_VD_ROOMBA_MAPPINGS']['Bin'],
                                str(stateData.bin_full))                                
        helper.send_auth_request(url,self.config)

    def do_self_test(self):
        pass

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
            return BaseService.get_html_gui(self, column_id)

        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        res = "State: " + self.handle.data.current_phase
        res = "Battery: " + self.handle.data.batPct
        column  = column.replace("<SERVICE_VALUE>", res)

        return column

            
if __name__ == '__main__':

    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = RoombaService("",config)
    test.init_service()

    time.sleep(40)
    
