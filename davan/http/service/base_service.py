'''
@author: davandev
'''

from davan.http.service.serviceIf import ServiceIf
import davan.util.constants as constants
from davan.http.service.alarm.Alarm import Alarm


class BaseService(ServiceIf):
    '''
    Default implementations of a few service methods  
    '''
    def __init__(self, service_name, service_provider, config):
        # Counter 
        self.invoked = 0
        self.error = 0
        # 
        self.service_name = service_name
        self.config = config
        self.services = service_provider
        self.is_running = False
        self.next_timeout =""
        self.last_timeout =""
        
    def handle_request(self, input):
        """
        Retrieve data from the input source and return an object.
        @param input 
        """
        return "Function not implemented"

    def get_name(self):
        """
        Return service name
        """
        return self.service_name
    
    def stop_service(self):
        """
        Default implementation when stopping service
        """
        self.is_running = False
        pass
    
    def start_service(self):
        """
        Default implementation when starting service
        """
        self.is_running = True
        pass
    
    def get_counters(self):
        """
        Return counters
        """
        return self.invoked, self.error

    def increment_invoked(self):
        """
        Increment counter when service is invoked
        """
        self.invoked +=1 

    def increment_errors(self):
        """
        Increment counter when error has occured
        """
        self.error +=1 

    def is_enabled(self):
        """
        Return True if service is enabled in configuration, false otherwise
        """
        return self.config[self.service_name+"Enabled"]
    
    def get_next_timeout(self):
        return  self.next_timeout

    def get_last_timeout(self):
        return  self.last_timeout
    
    def is_service_running(self):
        """
        Return True if service is running
        """
        return self.is_running
    
    def has_html_gui(self):
        """
        Override if service has gui
        """
        return False
    
    def raise_alarm(self, alarm_id, severence, title):
        alarm_mgr = self.services.get_service(constants.ALARM_SERVICE_NAME)
        if alarm_mgr != None:
            alarm = Alarm( alarm_id, severence, title )
            alarm_mgr.raise_alarm(alarm)

    def clear_alarm(self, id):
        alarm_mgr = self.services.get_service(constants.ALARM_SERVICE_NAME)
        if alarm_mgr != None:
            alarm_mgr.clear_alarm(id)
    
    def get_html_gui(self, column_ud):
        """
        Override and provide gui
        """
        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_ud))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        column = column.replace("<SERVICE_VALUE>", "<li>Enabled: " + str(self.config[self.service_name+"Enabled"]) + " </li>\n")
        return column

    def get_service(self, service_name):
        if service_name in self.services.services:
            return self.services.get_service(service_name)
        return None

    def services_started(self):
        pass
    def get_status(self):
        return ""
    
    def do_self_test(self):
        '''
        '''
        pass
    
    
    def init_service(self):
        '''
        '''
        pass