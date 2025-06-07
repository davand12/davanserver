'''
@author: davandev
'''

import logging 
import os
import urllib.request, urllib.parse, urllib.error

class TtsVoiceRssFactory():
    def __init__(self, config):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.config = config
        
    def generate_mp3(self, msg, mp3_file):
        ''' 
        Generate a mp3 file from the msg string.        
        Replace '_' with '%20' == whitespace
        @param msg message to translate
        @parm mp3_file output file where to store spoken msg.
        '''  
        encoded_msg = msg.replace("_", "%20")
        self.logger.debug("Encoded string [" + encoded_msg + "]")
        
        url = self.config['VOICERSS_URL'].replace("REPLACE_WITH_MESSAGE", encoded_msg)
        self.logger.debug("Url: ["+ url + "]")
        
        urllib.request.urlretrieve(url, mp3_file )
        return False