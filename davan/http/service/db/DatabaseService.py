'''
@author: davandev
'''

import logging
import os

import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.util import application_logger as log_manager
from davan.http.service.base_service import BaseService

import sqlite3
import hashlib
       
class DatabaseService(BaseService):
    '''
    '''
    def __init__(self, service_provider, config):
        '''
        Constructor
        Fix sqlite datasource in grafana
        mkdir -p /grafana
        mkdir -p /grafana/redirect
        sudo mount -r --bind /home/pi/davanserver/db/ /grafana/redirect
        '''
        BaseService.__init__(self, constants.DATABASE_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.db_path = config["DataBaseTablePath"]
        self.table_exist = False

    def has_html_gui(self):
        """
        Override if service has gui
        """
        return False

    def init_service(self):

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
                    
        #get the count of tables with the name
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='StatusTable' ''')

        #if the count is 1, then table exists
        if c.fetchone()[0]==1 :
            self.logger.debug('Database already exists.')
            self.table_exist = True
        else:
            c.execute('''CREATE TABLE StatusTable
             (tdate DATE, ttime TIME, name TEXT, status TEXT, enabled TEXT, success NUMERIC, failure NUMERIC, misc TEXT)''')
			
            
            #commit the changes to db			
            conn.commit()
            #close the connection
            conn.close()

    def services_started(self):
        self.logger.debug("All services started")
        if not self.table_exist:
            conn=sqlite3.connect(self.db_path)

            curs=conn.cursor()

            status ="initial"
            enabled="False"
            success=0
            fail=0
            misc="initial"
            for name, _ in self.services.services.items():
                curs.execute("""INSERT INTO StatusTable values(date('now'),
                time('now','localtime'), (?), (?), (?), (?), (?), (?))""", (name, status, enabled, success, fail, misc))

            #commit the changes to db			
            conn.commit()
            #close the connection
            conn.close()

        #self.update_status(name,"initial", "initial")

    def update_status(self, service_name, misc):
        conn=sqlite3.connect(self.db_path)

        curs=conn.cursor()

        service_handle = self.services.get_service(service_name)
        success, fail = service_handle.get_counters()
        name = service_handle.get_name()
        enabled = service_handle.is_service_running()
        status = service_handle.get_status()
#        curs.execute("""INSERT INTO StatusTable values(date('now'),
 #           time('now'), (?), (?), (?), (?), (?), (?))""", (name, status, enabled, success, fail, misc))
        curs.execute("""UPDATE StatusTable set 
            tdate = date('now'),
            ttime = time('now'), 
            name = (?), 
            status = (?), 
            enabled = (?), 
            success = (?), 
            failure = (?), 
            misc = (?) WHERE name==(?)""", (name, status, enabled, success, fail, misc, name))

        # commit the changes
        conn.commit()
        conn.close()        
        
if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=3)
    test = DatabaseService(None, config)
    test.update_status("test","mystatis",",mymisc")