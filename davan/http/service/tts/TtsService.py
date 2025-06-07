'''
@author: davandev
'''
 
import logging
import os
import shutil
import hashlib
import davan.util.cmd_executor as cmd_executor
from davan.http.service.base_service import BaseService
import davan.util.constants as constants 
from davan.http.service.tts.tts_engine_voicerss import TtsVoiceRssFactory 
from davan.http.service.tts.tts_engine_android import TtsEngineAndroid
from davan.http.service.tts.tts_engine_gtts import TtsVoiceGoogleTtsFactory
import traceback
from davan.util import helper_functions, constants

class TtsService(BaseService):
    '''
    classdocs
    sys.setdefaultencoding('latin-1')

    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.TTS_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.tts_engine = TtsVoiceGoogleTtsFactory(config)
        self.async_filename = None
        self.speakers=[0,1,2] #all, roxcore, rpi
        self.play_in_speakers = 0
        
    def handle_request(self, msg):
        '''
        Received request to generate speech from msg
        @param msg, received request 
        '''
        if ("tts=Completed" in msg):
            self.handle_ttsCompleted_callback()
        if "AlarmMsg" in msg:
            decoded_msg = msg.split('=')[1]
            # self.start(decoded_msg,"2") Roxcore hallway
            self.start(decoded_msg,"1")
        else:
            decoded_msg = msg.split('=')[1]
            self.start(decoded_msg,"1")

        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")    
    
    def start(self, msg, speakers, cache=False):
        '''
        Recevied request from Fibaro system to speak message.
        Check if message if already available, otherwise contact
        VoiceRSS to translate and get the mp3 file.
        @param msg to translate and speak.
        '''
        self.selected_speaker = speakers
        self.increment_invoked()

        if os.path.exists(self.config['SPEAK_FILE']):
            os.remove(self.config['SPEAK_FILE'])

        self.logger.info("Received request for new TTS message ["+ msg + "]")
        mp3_file = self.calculate_file_name(msg)
        
        isAsync = False
        if os.path.exists(self.config['MP3_ROOT_FOLDER'] + mp3_file):
            self.logger.debug("Using cached mp3 file")
        else:   
            self.logger.debug("Generate mp3 for [" + msg+"]")
            try:
                isAsync = self.tts_engine.generate_mp3(msg, mp3_file)
            except:
                self.logger.error(traceback.format_exc())
                helper_functions.send_telegram_message(
                                       self.config, 
                                       constants.FAILED_TO_GENERATE_TTS)
                self.increment_errors()

        
        if not isAsync:
            self.play_file(mp3_file)
        else:
            self.async_filename = mp3_file
            self.logger.info("Wait for TTS results")
                    
    def play_file(self, mp3_file):
        """
        Play the mp3 files in speakers
        """
        self.logger.info("Play file ["+ mp3_file + "] Speaker ["+ str(self.selected_speaker) + "]")
        speaker_service = self.config['SPEAKER_SERVICE']
        
        if str(self.selected_speaker) in self.config['SPEAKER_SERVICES'].keys():
            speaker_service = self.config['SPEAKER_SERVICES'][self.selected_speaker]
        
        speaker = self.services.get_service(speaker_service)
        speaker.handle_request(mp3_file,self.selected_speaker)

#         shutil.copyfile(self.config['MP3_ROOT_FOLDER'] + mp3_file, self.config['SPEAK_FILE'])
#         if self.play_in_speakers == 0 or self.play_in_speakers == 2:
#             cmd_executor.execute_block_in_shell(self.config['SPEAK_CMD'] + ' ' + 
#                                                 self.config['SPEAK_FILE'] , 
#                                                 self.config['SPEAK_CMD'])
#         if self.play_in_speakers == 0 or self.play_in_speakers == 1:
        # Play announcement
#        speaker = self.services.get_service(constants.ROXCORE_SPEAKER_SERVICE_NAME)
#        speaker.handle_request("announcement.mp3",self.selected_speaker)

        
    def handle_ttsCompleted_callback(self):
        """
        Received completed callback from TTS service  
        """
        self.logger.info("Received ttsCompleted callback") 
        if self.async_filename == None:
            return

        mp3_file = self.tts_engine.fetch_mp3(self.async_filename)
        self.play_file(mp3_file)
        self.async_filename = None        

    def calculate_file_name(self, msg):
        """
        Create the file name based on a md5 hash of the message
        """
        msg = msg.encode('utf-8')
        md5 = hashlib.md5()
        md5.update(msg)
        result = md5.hexdigest()
        mp3_file = result + ".mp3"
        self.logger.debug("Checksum of ["+str(msg)+"] = " + result)        
        return mp3_file
