'''
@author: davandev
'''

import logging
import os

import davan.config.config_creator as configuration
import davan.util.constants as constants
from davan.util import application_logger as log_manager
import datetime
import time
import sqlite3
import hashlib
       
class PumpMonitorDbHandle():
    '''
    '''
    def __init__(self,config):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.db_path = config['DataBaseTablePath']
        self.table_exist = False

    def init_db(self):
        '''
        Create db table if not already present.
        '''

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
                    
        #get the count of tables with the name
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='PumpMonitorServiceTable' ''')

        #if the count is 1, then table exists
        if c.fetchone()[0]==1 :
            self.logger.info('PumpMonitorServiceTable database already exists.')
            self.table_exist = True
        else:
            self.logger.info('Creating db table PumpMonitorServiceTable ')

            c.execute('''CREATE TABLE PumpMonitorServiceTable
             (datetime timestamp, invocations NUMBER, interval REAL)''')
            
            #commit the changes to db			
            conn.commit()
            #close the connection
            conn.close()
    
    def read_last_entry(self):
        '''
        Read last entry
        '''
        self.logger.info("Read invocation from PumpMonitorServiceTable db")
        conn=sqlite3.connect(self.db_path)

        curs=conn.cursor()
        curs.execute("SELECT invocations, interval FROM PumpMonitorServiceTable ORDER BY invocations DESC limit 1")
 
        return curs.fetchone()

    def insert(self, invocations, interval):
        '''
        Insert data into db table
        '''
        self.logger.info("Insert into PumpMonitorServiceTable db")
        conn=sqlite3.connect(self.db_path)

        curs=conn.cursor()
        curs.execute("""INSERT INTO PumpMonitorServiceTable values( (?), (?), (?))""", (time.time(), invocations, interval ))

        #commit the changes to db			
        conn.commit()
        #close the connection
        conn.close()