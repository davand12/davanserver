'''
@author: davandev
'''
# -*- coding: utf-8 -*- 

import logging
import os
import urllib.request, urllib.parse, urllib.error
import datetime
import telnetlib
import paramiko
import traceback
import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper

from davan.http.service.presence.AsusRouterDeviceStatus import AsusRouterDeviceStatus,\
    FAMILY, GUESTS, HOUSE
from davan.http.service.reoccuring_base_service import ReoccuringBaseService


'''
'''
class AsusRouterPresenceService(ReoccuringBaseService):
    '''
    This service is tested on an Asus router and relies on Telnet/ssh being enabled in the router.
    It is enabled in the router configuration.
    The presence of the monitored devices are determined on whether the device is 
    connected on the wifi network.
    The check is done by logging into the router via Telnet, and checking the connections
    using command "/usr/sbin/ip neigh" this gives a list of devices registered.
    Each device can be in state ESTABLISHED, STALE or FAILED.
    FAILED means that the device is not connected to the network. The states ESTABLISHED and STALE is
    interpreted as being available on wifi network.
    At state change a telegram message is sent to the receivers. Virtual device on Fibaro HC2 is also updated 
    with the state change.

    Set to failed : ip neighbour change to 192.168.2.30 dev br0 lladdr 3a:15:70:6c:c8:f4 nud failed
    '''

    def __init__(self, service_provider, config ):
        '''
        Constructor
        '''
        ReoccuringBaseService.__init__(self, constants.DEVICE_PRESENCE_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        logging.getLogger('paramiko.transport').setLevel(logging.CRITICAL)

        # Command to run on router to list available devices
        self.list_active_devices_cmd = "/usr/sbin/ip neigh"
        # Check status every 5th minute
        self.time_to_next_timeout = 300
        self.unknown_devices = []
        self.family_devices = {}
    
    def init_service(self):
        for key, value in list(self.config['FAMILY_DEVICES'].items()):
            self.family_devices[key]= AsusRouterDeviceStatus(key, value, FAMILY)
            
        self.guest_devices = {}
        for key, value in list(self.config['GUEST_DEVICES'].items()):
            self.guest_devices[key]= AsusRouterDeviceStatus(key, value, GUESTS)

        self.house_devices = {}
        for key, value in list(self.config['HOUSE_DEVICES'].items()):
            self.house_devices[key]= AsusRouterDeviceStatus(key, value, HOUSE)
    
    def do_self_test(self):
        try:
            self.fetch_active_devices()
        except Exception as e:
            self.logger.error(traceback.format_exc())

            msg = "Self test failed, failed to connect to router"
            self.logger.error(msg)
            self.raise_alarm(msg,"Warning",msg)

    def get_next_timeout(self):
        return self.time_to_next_timeout
    
    def handle_timeout(self):

        active_devices = self.fetch_active_devices()
        # Check family status
        self.check_device_group(self.family_devices, active_devices)
        # check guest status
        self.check_device_group(self.guest_devices, active_devices)
        # check house devices
        self.check_device_group(self.house_devices, active_devices)
        
    
    def check_unknown_devices(self, active_devices):
        for line in active_devices:
            if line.startswith("192."):
                items = line.split()
                if items[0] in list(self.family_devices.keys()):
                    continue
                elif items[0] in list(self.guest_devices.keys()):
                    continue
                elif items[0] in list(self.house_devices.keys()):
                    continue
                else:
                    if items[0] not in self.unknown_devices:
                        self.logger.debug("Unknown: "+ items[0])
                        self.unknown_devices.append(items[0])
                    if items[3] == "REACHABLE" or items[3] == "STALE":
                        self.logger.warning("Unknown active device : "+ str(items))
                        helper.send_telegram_message(self.config, "Unknown device is now active on network")

                        
 
    def check_device_group(self, monitored_devices, active_devices):
        # Reset changed state to false for all devices
        for ip, device in monitored_devices.items():
            monitored_devices[ip].changed = False
        
        self.update_presence(monitored_devices, active_devices)
        
        user_groups = self.group_user_devices(monitored_devices)
        self.check_user_devices(user_groups)
        self.reset_active_devices(monitored_devices)
    
    def group_user_devices(self, monitored_devices):
        user_groups = {}
        for _, device in list(monitored_devices.items()):
            if device.user in user_groups:
                user_groups[device.user].append(device)
            else:
                user_groups[device.user] = [device]
        return user_groups
    
    def reset_active_devices(self, monitored_devices):
        '''
        Fetch a list of all devices status from router. 
        @return list of found devices
        '''
        #self.logger.info('reset_active_devices')
        p = paramiko.SSHClient()
        p.set_missing_host_key_policy(paramiko.AutoAddPolicy())   # This script doesn't work for me unless this line is added!
        p.connect(self.config['ROUTER_ADRESS'], 
                  port=1025, 
                  username=self.config['ROUTER_USER'], 
                  password=self.config['ROUTER_PASSWORD'])
        for ip, _ in monitored_devices.items():
            reset_string = "/usr/sbin/ip neigh change to "+ip+" dev br0 nud failed"
            stdin, stdout, stderr = p.exec_command(reset_string)
            result = stdout.readlines()
            #self.logger.info("result:" +str(result))

        p.close()

    def check_user_devices(self, user_groups):
        for user, devices in list(user_groups.items()):
            if len(devices) == 1:
                if devices[0].changed:
                    devices[0].toString()
                    self.notify_change(devices[0])
            else:
                changedDevice = self.get_user_state_changed(devices[0],devices[1])
                if changedDevice != None:
                    changedDevice.toString()
                    self.notify_change(changedDevice)

    def get_user_state_changed(self, device1, device2):
        if device1.changed and device2.changed:
            if device1.active or device2.active:
                return device1
            elif not device1.active and not device2.active:
                return device1

        if device1.changed :
            if device1.active and not device2.active:
                return device1
            if not device1.active and not device2.active:
                return device1

        if device2.changed:
            if device2.active and not device1.active:
                return device2
            if not device2.active and not device1.active:
                return device2

        self.logger.debug("no device change or no change to update")
        return None

    def notify_change(self, device):
        '''
        Update Virtual device on Fibaro system and send Telegram messages
        with the changed device and status
        @param device device that changed state
        '''
        if device.type == FAMILY:
            url = helper.createFibaroUrl(self.config['UPDATE_DEVICE'], 
                                   self.config['FIBARO_VD_PRESENCE_ID'],
                                   self.config['FIBARO_VD_MAPPINGS'][device.user],
                                   device.active_toString())
            helper.send_auth_request(url,self.config)
        if (device.type == FAMILY or device.type == GUESTS):
            helper.send_telegram_message(self.config, device.user + " [" + device.active_toString() + "]")
        
    def fetch_active_devices(self):
        '''
        Fetch a list of all devices status from router. 
        @return list of found devices
        '''
        p = paramiko.SSHClient()
        p.set_missing_host_key_policy(paramiko.AutoAddPolicy())   # This script doesn't work for me unless this line is added!
        p.connect(self.config['ROUTER_ADRESS'], 
                  port=1025, 
                  username=self.config['ROUTER_USER'], 
                  password=self.config['ROUTER_PASSWORD'])
        
        stdin, stdout, stderr = p.exec_command(self.list_active_devices_cmd)
        result = stdout.readlines()
        p.close()
        return result

    def update_presence(self, monitored_devices, active_devices):
        '''
        Determine if any of the active devices in router is also
        monitored, then check device status
        '''
        for line in active_devices:
            if line.startswith("192."):
                items = line.split()
                if items[0] in list(monitored_devices.keys()):
                    self.logger.debug("Found a monitored device [" + items[0] +"]")
                    self.update_device_status(items, monitored_devices)

    def update_device_status(self, status, monitored_devices):
        '''
        Update device status of a monitored device
        @param status the status from router
        @param monitored_devices list of configured monitored devices
        '''
        device = monitored_devices[status[0]]
        device.toString()
        previous_status = device.active
        
        if("REACHABLE" in status or "STALE" in status):
            device.active = True
        elif "FAILED" in status:
            device.active = False
        if (previous_status == device.active): # No state changed
            self.logger.debug("No change of status for device[" + status[0] + "]")
            device.changed = False
            if device.active:
                device.last_active = str(datetime.datetime.now())
        else: # State is changed
            self.logger.debug("Change of status for device[" + status[0] + "]")
            device.changed = True
            if device.active:
                device.first_active = str(datetime.datetime.now())


    def get_announcement(self):
        '''
        Compile announcement to be read 
        '''
        announcement = ""
        for _, device in list(self.family_devices.items()):
            announcement += device.user + " är " + device.active_toString()+", "
        
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
         
        htmlresult = ["Family</br>\n"]
        
        for _,family in list(self.family_devices.items()):
            htmlresult.append(family.user  + "["+family.active_toString()+"]</br>\n")

        htmlresult += "\nGuests</br>\n"
        for _,guests in list(self.guest_devices.items()):
            htmlresult.append(guests.user  + "["+guests.active_toString()+"]</br>\n")
            
        htmlresult += "\nDevices</br>\n"
        for _,device in list(self.house_devices.items()):
            htmlresult.append(device.user  + "["+device.active_toString()+"]</br>\n")

        htmlresult += "\nUnknown Devices</br>\n"
        for device in self.unknown_devices:
            htmlresult.append(str(device)+"</br>\n")
        column = column.replace("<SERVICE_VALUE>", ''.join(htmlresult))
        
        return column
                
if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create('/home/pi/private_config.py')
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = AsusRouterPresenceService(config)
    test.timeout()
