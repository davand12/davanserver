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
       
class DatabaseHandle():
    '''
    grafana-cli plugins install frser-sqlite-datasource 
    sudo systemctl restart grafana-server.service
    mkdir -p /grafana
    mkdir -p /grafana/redirect
    sudo mount -r --bind /home/pi/davanserver/db/ /grafana/redirect
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
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='SpeedtestServiceTable' ''')

        #if the count is 1, then table exists
        if c.fetchone()[0]==1 :
            self.logger.info('SpeedtestServiceTable database already exists.')
            self.table_exist = True
        else:
            self.logger.info('Creating db table SpeedtestServiceTable ')

            c.execute('''CREATE TABLE SpeedtestServiceTable
             (datetime timestamp, upload TEXT, download TEXT, ping TEXT)''')
            
            #commit the changes to db			
            conn.commit()
            #close the connection
            conn.close()

    def insert(self, upload, download, ping):
        '''
        Insert data into db table
        '''
        self.logger.debug("Insert into SpeedtestServiceTable db")
        conn=sqlite3.connect(self.db_path)

        curs=conn.cursor()
        curs.execute("""INSERT INTO SpeedtestServiceTable values((?), (?), (?), (?))""", (time.time(), str(upload), str(download), str(ping) ))

        #commit the changes to db			
        conn.commit()
        #close the connection
        conn.close()