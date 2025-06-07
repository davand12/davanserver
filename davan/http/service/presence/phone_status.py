'''
@author: davandev
'''

import logging
import os
import datetime

class PhoneStatus(object):
    '''
    classdocs
    '''
    def __init__(self, user, mac_adress, ip_adress, iphone=False):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.user = user
        self.mac_adress = mac_adress.lower()
        self.ip_adress=ip_adress
        self.has_iphone = iphone
        
        self.status_changed = False
        self.phone_status = False
        self.wifi_last_active=""
        self.wifi_first_active=""
        self.wifi_status = False
        self.wifi_status_changed = False
        
        self.reporting_status=False
        self.reporting_status_changed=False
        self.reporting_last_active=""
        self.reporting_first_active=""
        now = datetime.datetime.now()
        self.expire_time = now - datetime.timedelta(minutes = 7)
        
    def set_wifi_status(self,status):
        self.wifi_status = status
        self.wifi_status_changed = True

    def set_reporting_status(self,status):
        self.reporting_status = status
        self.reporting_status_changed = True
    
    def toString(self):
        self.logger.debug("\nUser["+self.user+"] " + 
                          "mac["+self.mac_adress+"] " + 
                          "ip["+self.ip_adress+"]\n" + 
                          "StatusChanged["+str(self.status_changed)+"]\n" +
                          "StatusReporting["+str(self.reporting_status)+"] " +
                          "ReportingFirstActive["+self.reporting_first_active+"] " +
                          "ReportingLastActive["+self.reporting_last_active+"] " +
                          "ExpireTime["+str(self.expire_time)+"]\n" +
                          "StatusWifi["+str(self.wifi_status)+"] " +
                          "WifiFirstActive["+self.wifi_first_active+"] " +
                          "WifiLastActive["+self.wifi_last_active+"]\n")