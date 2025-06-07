import json
import logging
import time
import os
import traceback


import requests
import davan.config.config_creator as configuration
from davan.http.service.base_service import BaseService
import davan.util.constants as constants
from davan.http.service.smartlife.TuyaLight import TuyaLight
import davan.http.service.smartlife.TuyaUtil as TuyaUtil

REFRESHTIME = 60 * 60 * 12

class TuyaService(BaseService):
    def __init__(self, service_provider, config):
        '''
        dev_type=scene
---            color = 'pcfgMMAWFbbBqj4S' = trappa color

            off='iyBCrFKXuke9CG9O' = 1OFF
            soft =bla snabb blink = 'isdpZYNNdycsiqxc' = Trappa scene_1
            rainbow = vaxla rosa ljusbla '8XVre9V6gPEnhKUO' = Trappa Scene_2
            shine = blink rosa, = ''1dzMs1u1YCnKpkI7'' =  Trappa blink Scene3

            georgois = rulla flera farger == 'LU0pLuC5uymV3XvO' =  Trappa mjuk 4, scene_4
            leisure = ljusbla, 'HjC7E3W8ifxTfmRN' = Trappa Scene
---            party = orange/gul
---            reading = vit
---            night = gron/gul
             Trappa white - not working
        dev_type=light,
---            shine = blink rosa, = '83162473b4e62d1e085d' =Smart light srtio 2, colormode scene_4
            color = 'pcfgMMAWFbbBqj4S' =  Smart light srtio 2, trappa color
                    

        '''
        BaseService.__init__(self, constants.TUYA_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.session = TuyaUtil.TuyaSession()

    def init_service(self):
        self.session.username = self.config['TuyaUsername']
        self.session.password = self.config['TuyaPassword']
        self.session.countryCode = self.config['TuyaCountryCode']
        self.session.bizType = self.config['TuyaBizType']
        self.config_devices =  self.config['TuyaDevices']

        TuyaUtil.get_access_token(self.session)
        TuyaUtil.discover_devices(self.session)
        TuyaUtil.poll_devices_update(self.session)

    def parse_request(self, msg):
        '''
        @param msg, received request
        '''
        msg = msg.split('?')
        res = msg[1].split('=')
        return res[0], res[1]

    def handle_request(self, msg):
        '''
        Light on/off request received from Fibaro system,
        forward to Tuya ledstrips.
            scene_name, action = self.parse_request(msg)
            self.increment_invoked()
            self.logger.info("Received request Scene["+scene_name+"] Action["+action+"]")
            if scene_name in self.config_devices.keys():
                if action =="Toggle":
                    device = TuyaUtil.get_device_by_name(self.session, scene_name)
                    if device.data['state'] == 'true':
                        scene_name = self.config_devices[scene_name][1]
                        device.data['state'] = 'false'
                    else:    
                        scene_name = self.config_devices[scene_name][0]
                        device.data['state'] = 'true'
            else:
                for _, scenes in self.config_devices.items():
                    if(scene_name in scenes):
                        break
                    
            device = TuyaUtil.get_device_by_name(self.session, scene_name)
            device.turn_on()
            device.turn_on()
 
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            self.raise_alarm(constants.TUYA_NOT_ANSWERING, "Warning", constants.TUYA_NOT_ANSWERING)

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")
                    
        '''
        try:

            scene_name, action = self.parse_request(msg)
            self.increment_invoked()
            self.logger.info("Received request Scene["+scene_name+"] Action["+action+"]")
            if scene_name not in self.config_devices:
                self.logger.warning("Scene["+scene_name+"] not found!")
                return
            if action =="Toggle":
                device = TuyaUtil.get_device_by_name(self.session, scene_name)
                if device.data['state'] == 'true':
                    scene_name = scene_name.replace("Light","off")
                    device.data['state'] = 'false'
                else:    
                    scene_name = scene_name.replace("Light","Color")
                    device.data['state'] = 'true'
            device = TuyaUtil.get_device_by_name(self.session, scene_name)
            device.turn_on()
            device.turn_on()
 
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            self.raise_alarm(constants.TUYA_NOT_ANSWERING, "Warning", constants.TUYA_NOT_ANSWERING)

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")
            