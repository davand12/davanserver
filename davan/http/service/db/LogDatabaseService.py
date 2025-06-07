'''
@author: davandev
result = client.query('select value from cpu_load_short;')
'''

import logging
import os
from influxdb import InfluxDBClient

import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.util import application_logger as log_manager
import datetime
import time
from davan.http.service.base_service import BaseService

class LogDatabaseService(BaseService):
    '''
    '''
    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.DATABASE_LOGS_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.db_path = config["DataBaseTablePath"]
        self.table_exist = False
        self.client = None
        self.last_record = None

    def has_html_gui(self):
        """
        Override if service has gui
        """
        return False

    def init_service(self):
        '''
        Create db table if not already present.
        '''

        self.client = InfluxDBClient('localhost', 8086, 'davan', 'davand', 'logging')
        self.client.create_database('logging')
        self.client.switch_database('logging')
        for handler in logging.root.handlers:
            handler.addFilter(self.on_log)


    def on_log(self, record):
        if self.last_record == None:
            pass
        elif record.getMessage() != self.last_record.getMessage(): 
            self.insert(record.levelname, record.name, record.getMessage())
        self.last_record = record    
        return True


    def insert(self, level, classname, message):
        '''
        Insert data into db table
        '''
        json_payload = []
        data = {
            "measurement":"logs2",
            "tags": {
              "level": level,
              "class": classname
            },
            "time": datetime.datetime.now(),
            "fields": {
               "message": message
            },
        }
        json_payload.append(data)   

        self.client.write_points(json_payload)

def on_log2(record):
    print(record.getMessage())
    return True

if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = LogsDbHandle(config)
    test.init_db()
    test.insert("2021-06-06T18:02:00","info","mytestclass3", "This is a test message3")
    test.insert("2021-08-06T18:02:00","debug","mytestclass", "This is a test message13")
    test.insert("2022-10-06T18:02:00","info","mytestclass2", "This is a test message23")
    test.insert("2022-09-06T18:02:00","debug","mytestclass", "This is a test message133")