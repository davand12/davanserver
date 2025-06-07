'''
@author: davandev
'''

import abc

class ServiceIf(object, metaclass=abc.ABCMeta):
    '''
    Interface for services
    '''
    
    @abc.abstractmethod
    def handle_request(self, input):
        """
        Abstract method to override to handle received request.
        """
        return
    @abc.abstractmethod
    def get_name(self):
        """
        Abstract method returns name of the service  
        """
        return ""

    @abc.abstractmethod
    def get_status(self):
        """
        Abstract method returns status of the service  
        """
        return ""
    
    
    @abc.abstractmethod
    def stop_service(self):
        '''
        Abstract method to stop service
        '''
        pass
    
    @abc.abstractmethod
    def start_service(self):
        '''
        Abstract method to start service
        '''
        pass
    
    @abc.abstractmethod
    def services_started(self):
        '''
        Abstract method indicate all services started
        '''
        pass
    
    @abc.abstractmethod
    def is_service_running(self):
        '''
        Abstract method to determine if service is running
        '''
        pass
    @abc.abstractmethod
    def do_self_test(self):
        '''
        Abstract method, service should if applicable perform self test 
        and report any errors
        '''
        pass
    
    @abc.abstractmethod
    def init_service(self):
        '''
        Abstract method to initialize service
        '''
        pass