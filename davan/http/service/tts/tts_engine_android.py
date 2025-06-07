'''
@author: davandev
'''

import logging 
import os
import urllib.request, urllib.error, urllib.parse
import davan.util.cmd_executor as executor
import shutil
import traceback
from davan.util import helper_functions, constants

class TtsEngineAndroid():
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
        encoded_msg = helper_functions.encode_message(msg)
        result = urllib.request.urlopen(self.config["TTS_GENERATOR_CREATE_URL"] + "="+encoded_msg).read()

        return True
    
    def fetch_mp3(self, filename):
        '''
        Download the generated tts file, and convert to mp3.
        @param filename name of the file to download should get
        '''
        self.logger.info("Downloading tts file ["+filename+"]") 
        result = urllib.request.urlopen(self.config["TTS_GENERATOR_FETCH_URL"]).read()
        wav_file = self.config['TEMP_PATH'] + "/tmp.wav"

        if (not os.path.exists(self.config['TEMP_PATH'])):
            os.mkdir(self.config['TEMP_PATH'])
                    
        if (os.path.exists(wav_file)):
            os.remove(wav_file)
            
        fd = open(wav_file, 'wb')
        fd.write(result)
        fd.close()
        
        command = "lame -f " + wav_file
        executor.execute_block(command, "lame", False)
        mp3_file = wav_file.replace('wav','mp3')
        shutil.move(mp3_file, self.config['MP3_ROOT_FOLDER'] + filename)
        return filename
