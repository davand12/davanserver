'''
@author: davandev
'''
# coding: utf-8

import logging
import os
import traceback
import sys
import urllib
import json
import time

import davan.util.helper_functions as helper
import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.util import cmd_executor as cmd_executor
from davan.http.service.base_service import BaseService
import davan.http.service.tradfri.TradfriCommands as commands


class Device():
    def __init__(self, name, id, type_name, type_id, type_id2, off, on):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.name = name
        self.device_id = id 
        self.type_name = type_name
        self.type_id = type_id
        self.type_id2 = type_id2
        self.off_value = off
        self.on_value = on
        self.logger.info(self.toString())

    def get_value(self, action):
        if action == 'on':
            return self.on_value
        return self.off_value

    def toString(self):
        return "Name[ " + self.name + " ] "\
            "DeviceId[ " + self.device_id + " ] "\
            "DeviceTypeName[ " + self.type_name + " ] "\
            "DeviceTypeId[ " + self.type_id + " ] "\
            "Id[ " + self.type_id2 + " ] "\
            "Off[ " + self.off_value + " ] "\
            "On[ " + self.on_value + " ] "

    
class DeviceType():

    def __init__(self, name, id, id2, off, on):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.name = name
        self.id = id 
        self.id2 = id2
        self.off_value = off
        self.on_value = on
        self.logger.info(self.toString())

    def toString(self):
        return "Name[ " + self.name + " ] "\
            "DeviceId[ " + self.id + " ] "\
            "Id[ " + self.id2 + " ] "\
            "Off[ " + self.off_value + " ] "\
            "On[ " + self.on_value + " ] "


class TradfriService(BaseService):
    '''
    classdocs
    coap-client -m put -u tradfri-pi-bash -k GfInzH6JGn06qbab -B 30 coaps://192.168.2.4:5684/15001/65549 -e '{ "15015" : [{ "5536" : 10 }] }'
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.TRADFRI_SERVICE_NAME, service_provider, config)                    
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.STATES = {"off":0 , "on":1 }
        self.devices = {}
    
    def init_service(self):
        self.get_devices_from_config()
        
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
        forward to Tradfri gateway.
        '''
        try:
            device_name, action_str = self.parse_request(msg)
            self.logger.debug("Action:" +action_str)
             
            if device_name not in self.devices.keys():
                self.logger.error("Cannot find the device_id " + device_name + " in configured devices")
                return
            self.increment_invoked()

            device = self.devices[device_name]
            
            if device.type_name == "GroupController":
                self.logger.info('Handle groups')
                ids = device.device_id
                ids = ids.replace("[","")
                ids = ids.replace("]","")
                for name in ids.split(' '):
                    self.logger.info("Id:" + name)
                    item = self.devices[name]
                    if action_str == "toggle":
                        new_state = self.get_toggled_device_state(item)
                    else:
                        new_state = item.get_value(action_str)
        
                    self.logger.info("Device ["+device_name+"] NewState:" + str(new_state))
                    self.set_state(name, new_state)
                    #self.performAction(item,action_str)
                    #time.sleep(1000)
            else:
                self.performAction(device,action_str)
        
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
            helper.send_telegram_message(self.config, str(e)) 
            self.raise_alarm(constants.TRADFRI_NOT_ANSWERING, "Warning", constants.TRADFRI_NOT_ANSWERING)

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")

    def performAction(self, device, action_str):
        if device.name == "all":
            self.toggle_all_device_states(action_str)
            return
        if action_str == "toggle":
            action = self.get_toggled_device_state(device)

        elif action_str.startswith("toggleDimmer"):
            action = self.get_toggled_dimmer_state(device)
            self.logger.info("Dimmer state:" + action)

        elif action_str.startswith("setvalue"):
            res = action_str.split('+')
            action = res[1]
            
        else:
            action = device.get_value(action_str)
        
        self.logger.info("Device[" + device.name + "] Action[" + str(action_str) + "]")
        self.set_state(device.name, action)

    def set_state(self, device_name, state):
        '''
        Set the state of the device
        @param device_name, name of device
        @param state, the wanted state
        '''
        if device_name not in self.devices.keys():
            self.logger.error("Cannot find the device_id " + device_name + " in configured devices")
            return
        
        device = self.devices[device_name]
        self.logger.debug("Change state of device " + device_name + "  New state[" + str(state) + "]")
        commands.set_state(self.config, device, state)
        
    def get_toggled_device_state(self, device):
        '''
        Determine the state of the device, then return the opposite state
        @param device_name, name of device
        '''
        
        try:
            current_state = commands.get_state(self.config, device)
            
            self.logger.debug("State of " + device.name + " = " + str(current_state))
            
            if current_state == str(device.off_value) or current_state == False:
                return device.on_value
            return device.off_value
        except Exception as e:
            self.logger.debug("Caught exception: " + str(e))
            raise Exception("Misslyckades att hamta status for "+ str(device.name))
            
    def get_toggled_dimmer_state(self, device):
        '''
        Determine the dimmer state of the device, then return the opposite configured min/max
        @param device_name, name of device
        '''
        
        try:
            current_state = commands.get_dimmer_state(self.config, device)
            
            self.logger.debug("State of " + device.name + " = " + str(current_state))
            
            if int(current_state) < int(device.on_value) :
                return device.on_value
            return device.off_value
        except Exception as e:
            self.logger.debug("Caught exception: " + str(e))
            raise Exception("Misslyckades att hamta status for "+ str(device.name))

    def toggle_all_device_states(self, action_str):
        '''
        Iterate through all devices of type socket and driver controller and perfom action
        '''
        self.logger.debug("Toggle all device states[" + str(action_str) + "]")        
        items = self.devices.values()
        for item in items:
            if item.type_name =='SocketController':
                self.logger.info("Device[" + item.name + "] Action[" + str(action_str) + "]")
                self.set_state(item.name, item.get_value(action_str))


    def list_all_devices(self):
        '''
        List all devices configured in Tradfri Live
        '''
        self.logger.info("List all Tradfri devices 1")
        devices = commands.get_status(self.config)
        self.logger.info("Found devices : " + str(devices))

    def get_devices_from_config(self):
            '''
            Parse all configured tradfri devices
            '''
            
            device_types = {}
            types = self.config['TRADFRI_DEVICE_TYPES']
            for types in types:
                items = types.split(",")          
                device_types[items[0]] = DeviceType(items[0].strip(), items[1].strip(), items[2].strip(), items[3].strip(), items[4].strip())
                
            self.devices['all'] = Device('all','','','', '','','')

            configuration = self.config['TRADFRI_DEVICES']
            for device in configuration:
                items = device.split(",")          
                type = device_types[items[2].strip()]
                
                self.devices[items[0].strip()] = Device(items[0].strip(),  # DeviceName
                                                        items[1].strip(),  # DeviceId,
                                                        type.name,  # DeviceTypeName
                                                        type.id,  # DeviceTypeId
                                                        type.id2,  # DeviceTypeId
                                                        type.off_value,  # Off value 
                                                        type.on_value)
                    
    def log_devices(self):
        device_string = ""
        for _, device in self.devices.items():
            device_string += device.toString() + "\n"
        
        self.logger.debug(device_string)
        return device_string

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
        self.list_all_devices()
        devices = self.log_devices()
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", str(devices))
        return column
        
if __name__ == '__main__':
    from davan.util import application_logger as app_logger
    config = configuration.create()
    
    app_logger.start_logging(config['LOGFILE_PATH'], loglevel=4)
    
    test = TradfriService("", config)
    # test.get_toggle_device_state("KITCHEN")
    devices = test.list_all_devices()
    #dev = [65601,65597,65540,65577,65579,65605,65606,65591,65593,65563,65547,65585,65545,65580,65604,65546,65599,65541,65578,65544,65539,65592,65542,65581,65603,65583,65598,65560,65586]
    dev = [65592,65603,65599,65597,65583,65546,65541,65542,65539,65540,65580,65601,65598,65604,65581,65585,65579,65545,65578,65605,65547,65544,65577,65563,65560,65586,65591,65593,65606,65607,65608]

    #dev = []
    # # #test.handle_request("TradfriService?Datarum=toggle")
    for device in dev:
        commands.get_device_status(config, str(device))
    # test.perform("KITCHEN","1"e