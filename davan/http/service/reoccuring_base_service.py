'''
@author: davandev
'''
import datetime
import time
from davan.http.service.base_service import BaseService
import davan.util.constants as constants
from threading import Thread,Event
import traceback

class ReoccuringBaseService(BaseService):
    '''
    Default implementations of a few service methods  
    '''
    def __init__(self, service_name, service_provider, config):
        BaseService.__init__(self, service_name, service_provider, config)
        self.event = None
        self.time_at_timeout = ""
            
    def stop_service(self):
        '''
        Stop the service
        '''
        self.logger.debug("Stopping service")
        if self.is_running:
            self.is_running = False
            self.event.set()

    def start_service(self):
        '''
        Start a timer that will pop repeatedly.
        @interval time in seconds between timeouts
        @func callback function at timeout.
        ''' 
        # See http://bugs.python.org/issue7980
        time.strptime("01:00", '%H:%M')
        _ = datetime.datetime.strptime("01:00", '%H:%M')
        # End of workaround

        #self.logger.info("Starting re-occuring service ")
        self.event = Event()

        def loop():
            self.is_running = True
            self.next_timeout = self.get_next_timeout()    
            while not self.event.wait(self.next_timeout):
                try:                    
                    current_time = datetime.datetime.now()
                    next_time  = current_time + datetime.timedelta(0,self.next_timeout)
                    self.time_at_timeout = next_time.strftime("%Y%m%d-%H:%M:%S")
                    self.increment_invoked()
                    self.handle_timeout()
                except:
                    self.logger.error(traceback.format_exc())   
                    self.increment_errors()
                finally:
                    self.next_timeout = self.get_next_timeout()  
                    self.last_timeout = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                    db = self.get_service(constants.DATABASE_SERVICE_NAME)
                    db.update_status(self.get_name(),self.time_at_timeout)   

        Thread(target=loop, name=self.service_name).start()    
        return self.event.set
    

    def handle_timeout(self):
        """
        Default implementation when timeout occur
        """
        self.logger.error("Default implementation")
        pass

    def get_next_timeout(self):
        """
        Default implementation 
        """
        self.logger.error("Default implementation")
        pass