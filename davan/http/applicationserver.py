"""
@author: davandev
"""
#!/bin/env python
import logging
import os
import time
import datetime
#import datetime.datetime.strptime
#import datetime.datetime
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import socket
import http.server#
import http.client
import cgi
import argparse
import traceback
import signal
import sys
import builtins


import davan.util.application_logger as log_manager
import davan.config.config_creator as config_factory
import davan.util.helper_functions as helper
import davan.util.constants as constants

from davan.http.ServiceInvoker import ServiceInvoker
global services

global logger
logger = logging.getLogger(os.path.basename(__file__))

class RunningServerException(Exception):
    """
    Exception raised when an existing distribution server is discovered on the host
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# Custom handler to handle http requests received in server.
class CustomRequestHandler(BaseHTTPRequestHandler):
    """
    Request handler that handles incoming requests.
    """

    def do_POST(self):
        """
        Handles POST requests.
        Currently not implemented
        """
        try:
            #logger.debug("Received POST request from external host : " + self.address_string() + " Path "+ self.path)
            
            if(self.path.endswith("ImouCameraService")):
                self.path = "ImouCameraService"

            service = services.get_service(self.path)
            if not service == None:
                content_len = int(self.headers.get('Content-Length'))
                data = self.rfile.read(content_len)
                #logger.info("Received post "+str(data))
                result_code, mime_type, result = service.handle_request(data)

                self.send_response(result_code)    
                self.send_header('Content-type',    mime_type)
            else:
                self.send_error(404, 'File Not Found: %s' % self.path)

        except IOError:
            logger.warning("Unexpected post request:"+str(self.path))

            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_GET(self):
        '''
        Handle GET requests
        '''
        try:
            global services
            service = services.get_service(self.path)
            if not service == None:
                result_code, mime_type, result = service.handle_request(self.path)
                db = services.get_service(constants.DATABASE_SERVICE_NAME)
                db.update_status(service.get_name(),"")

                self.send_response(result_code)    
                self.send_header('Content-type',    mime_type)
                if result is not None:
                    self.send_header('Content-Length', len(result))
                    self.end_headers()
                    #self.wfile.write(result.encode())
                    self.wfile.write(result)
                else:
                    self.end_headers()

                return
            
            # Another server is started, terminate this one.
            elif self.path.endswith("seppuku"):
                logger.critical("Received request to shut down server")
                if builtins.davan_services.is_running():
                    builtins.davan_services.stop_services()
                    self.send_response(200)
                    self.send_header('Content-type',    'text/html')
                    self.end_headers()
                    self.wfile.write(b"hai")
                else:
                    self.send_response(200)
                    self.send_header('Content-type',    'text/html')
                    self.end_headers()
                    self.wfile.write(b"hai")
                    self.server.socket.close()
            else:
                logger.warning("Unexpected get request:"+str(self.path))
                self.send_error(404, 'File Not Found: %s' % self.path)

            return

        except :
            logger.warning("Unexpected request:["+str(self.path)+"] from [" +str(self.client_address[0]) + "]" )
            logger.error(traceback.format_exc())
            self.send_error(404, 'File Not Found: %s' % self.path)

    def log_message(self, format, *args):
        return


class ApplicationServer(ThreadingMixIn, http.server.HTTPServer):
    pass
# Send a request to running server to shutdown.
def _tear_down_running_server(config):
    """
    Sends a request to an instance of the server running on the same host 
    requesting it to shutdown.
    @param port: The port where to send the tear down request.
    """
    logger.debug("Tear down existing server on [" + config["SERVER_ADRESS"] + "]" +
                 " port[" + str(config["SERVER_PORT"]) + "]")

    conn1 = http.client.HTTPConnection(config["SERVER_ADRESS"] + ":" + str(config["SERVER_PORT"]))
    conn1.request("GET", "/seppuku")
    r1 = conn1.getresponse()
    response_msg = r1.read()
    if response_msg == "hai":
        conn1.request("GET", "/seppuku")
        r1 = conn1.getresponse()
        response_msg = r1.read()


# Try to start the server, 
def start_server(configuration):
    """
    Starts the server on the provided port.
    Raises exception if an instance is already running on the host
    @param port: The port that the server listens to
    """
    try:
        helper.debug_big("Starting server")        
        time.strptime("01:00", '%H:%M')
        _ = datetime.datetime.strptime("01:00", '%H:%M')
        global services
        services = ServiceInvoker(config)
        services.discover_services()
        services.start_services()
        # ugly way to share services
        builtins.davan_services = services
        server = ApplicationServer(('', config["SERVER_PORT"]), CustomRequestHandler)
        helper.debug_big("Server started on [" + str(config["SERVER_ADRESS"]) + ":" + str(config["SERVER_PORT"]) + "] ")        
        while 1:
            server.handle_request()
            if not builtins.davan_services.is_running():
                server.server_close()
                logger.critical("Stopping server")
                sys.exit(1)
        
    except socket.error as xxx_todo_changeme:
        (value, message) = xxx_todo_changeme.args
        if value == 98:  # Address port already in use
            helper.debug_big("Failed to start server with message" +
                         " [" + message + "]")

            raise RunningServerException("Port is already in use")
        else:
            logger.error("Failed to start server")
    
def _parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start",
                    help="Start server",
                    action="store_true")
    parser.add_argument("-o", "--stop",
                    help="Stop server",
                    action="store_true")
    parser.add_argument("-d","--debug",
                    help="Enable debug",
                    action="store_true",
                    default=False) 
    parser.add_argument("-p","--privateconfig",
                    help="Configuration file with private data",
                    action="store",
                    default="/home/pi/private_config.py") 
    args = parser.parse_args()
    return args

def handler(signum, frame):
    logger.info("Caught Ctrl+c, stopping server")
    global services
    services.stop_services()    
    sys.exit(1)

if __name__ == '__main__':
    _ = datetime.datetime.strptime("01:00", '%H:%M')

    args = _parse_arguments() 
    config = config_factory.create(args.privateconfig)
    if args.debug: 
        #log_manager.start_file_logging(config["LOGFILE_PATH"])

        helper.debug_formated(config)
        log_manager.start_logging(config["LOGFILE_PATH"],loglevel=4)
    else:
        log_manager.start_file_logging(config["LOGFILE_PATH"], config["LOGLEVEL"])

    try:
        if args.stop:
            _tear_down_running_server(config)
            logger.debug("Shutting down existing server")
            exit(1)
        else:
            signal.signal(signal.SIGINT, handler)
            start_server(config)
    except RunningServerException:  # Running server found
        if _tear_down_running_server(config):
            time.sleep(2)  # wait for running server to shutdown
            start_server(config)
        else:
            logger.error("Failed to terminate the running server")
    except socket.error:
        logger.error("Server not running")


