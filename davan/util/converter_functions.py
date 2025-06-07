'''
@author: davandev
'''
import os
import logging
import davan.util.cmd_executor as executor
global logger
logger = logging.getLogger(os.path.basename(__file__))

def ogg_to_wav(config, ogg_file):
    if (not os.path.exists(config['TEMP_PATH'])):
        os.mkdir(config['TEMP_PATH'])
                
    if (os.path.exists(config['MP3_ROOT_FOLDER'] + "telegram_voice.wav")):
        os.remove(config['MP3_ROOT_FOLDER'] + "telegram_voice.wav")
        
    command = "opusdec " + ogg_file + " " + config['MP3_ROOT_FOLDER'] + "telegram_voice.wav"
    executor.execute_block(command, "opusdec", False)
    return "telegram_voice.wav"