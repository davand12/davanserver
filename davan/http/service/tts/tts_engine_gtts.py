'''
@author: davandev
'''

import logging 
import os
import urllib.request, urllib.parse, urllib.error
import gtts
import davan.config.config_creator as configuration

class TtsVoiceGoogleTtsFactory():
    def __init__(self, config):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.config = config
        
    def generate_mp3(self, msg, mp3_file):
        ''' 
        Generate a mp3 file from th e msg string.        
        Replace '_' with '%20' == whitespace
        @param msg message to translate
        @parm mp3_file output file where to store spoken msg.
        '''  
        self.logger.info("Generate tts")

        decoded_msg = urllib.parse.unquote(msg)
        self.logger.debug("Encoded string [" + decoded_msg + "]")
        
        self.logger.info("Start generate")
        tts = gtts.gTTS(text=str(msg), lang='sv')
        
        save_file = self.config['MP3_ROOT_FOLDER'] + mp3_file
        self.logger.info('saving MP3 file '+save_file) 
        tts.save(str(save_file))

        return False

if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create('/home/pi/private_config.py')
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = TtsVoiceGoogleTtsFactory(config)
    test.generate_mp3("testar att gemerae","/dev/shm/speak.mp3")
