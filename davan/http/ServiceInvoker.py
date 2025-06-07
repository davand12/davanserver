'''
@author: davandev
'''

import os
import logging
import imp
import time
import re
import traceback

import davan.config.config_creator as app_config
import davan.util.application_logger as app_logger
import davan.util.constants as constants

class ServiceInvoker(object):
    '''
    Service Handler module, scanning for services,
    '''
    def __init__(self, configuration):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.services ={}
        self.expression = re.compile(r'\w+')
        self.config = configuration
        # Determine if services are started
        self.running = False
        
    def is_running(self):
        return self.running
    
    def discover_services(self):
        """
        Scan service folder for all matching services.
        """
        self.logger.info("Discover services")
        for root, _, files in os.walk(self.config['SERVICE_PATH']):
            for service_file in files:
                if (service_file.endswith(".py") and 
                    not service_file.endswith("__init__.py") and 
                    not service_file.endswith("serviceIf.py") and
                    not service_file.endswith("base_service.py")):
                        module_name = service_file.replace(".py","")
                        #mod = imp.load_compiled(module_name,os.path.join(root, service_file))
                        mod = imp.load_source(module_name, os.path.join(root, service_file))
                        self.logger.debug("ModuleName:"+module_name)

                        try:    
                            attributes = getattr(mod, module_name)
                            service = attributes(self, self.config)
                            self.services[service.get_name()] = service
                            self.logger.debug("Discovered service [" + module_name + "] Service key[" + service.get_name()+"]")
                        except :
                            pass
                            self.logger.error(traceback.format_exc())
        self.logger.info("Discovered services")                        
        return self.services
    
    def start_services(self):
        """
        Start all services that are enabled in configuration
        """
        self._init_services()
        self._test_services()
        self._start_services()
        self._wait_for_start()
        self._notify_services_started()
        

    def _notify_services_started(self):    
        self.logger.info("Notify service started")
        for _, service in self.services.items():
            service.services_started()

    def _test_services(self):    
        self.logger.info("-- Test services --")
        for _, service in self.services.items():
            if service.is_enabled():
                service.do_self_test()

    def _init_services(self):
        self.logger.info("-- Initializing services --")
        for name, service in self.services.items():
            if service.is_enabled():
                service.init_service()
            else:
                self.logger.debug("Service " + name + " is disabled")
        self.logger.debug("All configured services initialized")
    
    def _start_services(self):
        self.logger.info("-- Starting services --")
        for name, service in self.services.items():
            if service.is_enabled() and not service.is_service_running():
                service.start_service()
            else:
                self.logger.debug("Service " + name + " is disabled")
        self.logger.debug("All configured services started")

    def _wait_for_start(self):
        while True:
            wait_for_service = False
            for name, service in self.services.items():
                if service.is_enabled() and not service.is_service_running():
                    self.logger.info("waiting for " +name )
                    wait_for_service = True
            if wait_for_service:
                time.sleep(2)
            else:
                break
        self.running = True 


    def get_service(self, service):
        """
        @param service, name of selected service
        @return: service matching service name
        """
        result = self.expression.findall(service)[0]
        
        if result in self.services:
#            self.logger.debug("Invoking service: ["+ result+"]")
            return self.services[result]
        elif service.endswith(constants.MP3_EXTENSION) or service.endswith(constants.MP3_EXTENSION1):
#            self.logger.debug("Invoking service: [mp3]")
            return self.services[constants.MP3_SERVICE_NAME]
        elif service.endswith(constants.OGG_EXTENSION) or service.endswith(constants.OGG_EXTENSION1):
#            self.logger.debug("Invoking service: [ogg]")
            return self.services[constants.MP3_SERVICE_NAME]
        elif service.endswith(constants.HTML_EXTENSION) or service.endswith(constants.CSS_EXTENSION):
#            self.logger.debug("Invoking service: [html]")
            return self.services[constants.HTML_SERVICE_NAME]
        
        # No service found
        self.logger.debug("No service ["+str(service)+"] found")
        
        return None
    
    def stop_all_except(self, service_name):
        self.logger.info("Stopping all services")

        for service in self.services.values():
            self.logger.debug("Stopping: " + str(service.get_name()))
            if service.service_name == service_name:
                continue
            service.stop_service()

        self.logger.info("All started services stopped")

    def start_all_except(self, service_name):
        self.logger.info("Starting all services")

        for service in self.services.values():
            self.logger.debug("Starting: " + str(service.get_name()))
            if service.is_enabled() and not service.is_service_running():
                if service.service_name == service_name:
                    continue
                service.start_service()

        self.logger.info("All started services started")
                    
    def stop_services(self):
        """
        Stop all services
        """
        self.logger.info("Stopping all services")

        for service in self.services.values():
            #self.logger.debug("Stopping: " + str(service.get_name()))
            service.stop_service()
        self.running = False
        self.logger.info("All started services stopped")
       
if __name__ == '__main__':
    config = app_config.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    # test = ServiceInvoker()
    # test.invoke_services()
    # test.get_service("/tts=234?")
    # test.get_service("/presence?name=david")
    # time.sleep(10)
    # test.logger.info("Stopping thread")
    # test.stop_services()
