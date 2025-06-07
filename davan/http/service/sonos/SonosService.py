'''
@author: davandev
'''

import logging
import os
import urllib.request, urllib.parse, urllib.error
import traceback


import davan.config.config_creator as configuration
from davan.util import application_logger as app_logger
from davan.http.service.base_service import BaseService
import davan.util.constants as constants 
import davan.http.service.sonos.SonosCommands as commands

from soco import SoCo

class SonosSpeaker():
    def __init__(self, id, slogan, address, default_speaker, play_announcement):
        self.logger = logging.getLogger(os.path.basename(__file__))

        self.id = id 
        self.slogan = slogan
        self.address = address
        self.default_speaker = default_speaker
        self.play_announcement = play_announcement
#        self.logger.info(self.toString())

    def toString(self):
        return "Slogan[ "+self.slogan+" ] "\
            "Id[ "+self.id+" ] "\
            "Address[ "+self.address+" ] "\
            "Speaker[ "+self.default_speaker+" ] "\
            "Announcement[ "+self.play_announcement+" ]"

class SonosService(BaseService):
    '''
    classdocs
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        /Sonos?msg=sdfsa_asdfdf_asdf
        '''
        BaseService.__init__(self, constants.SONOS_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.speakers = {}
    
    def init_service(self):        
        self.get_speakers_from_config()
        
    def _parse_request(self, msg):
        return self.start(msg.split('=')[1])
    
    def handle_request(self, msg, speaker_id="0"):
        '''
        Play mp3 file on sonos speaker.
        @param msg, file to play 
        '''
        try:
            if speaker_id == "2":
                for _,speaker in list(self.speakers.items()):
                    self.logger.info("Play in speaker[" + self.speakers[speaker_id].slogan+"]")
                    
                    sonos = SoCo(self.speakers[speaker_id].address)
                    sonos.play_uri(msg,"Speech")
            else:
                self.logger.info("Play in speaker[" + self.speakers[speaker_id].slogan+"] Address[" +self.speakers[speaker_id].address+"]" )

                sonos = SoCo(self.speakers[speaker_id].address)
                uri = 'http://' + self.config['SERVER_ADRESS'] +':' + str(self.config['SERVER_PORT']) + '/mp3=' + msg
                sonos.play_uri(uri,"Speech")

#                speaker_address = "http://" + self.speakers[speaker_id].address + ":" + self.config['ROXCORE_PORT_NR']
#                speaker_address = "http://" + speaker.address + ":" + self.config['ROXCORE_PORT_NR']
#                self._send_to_speaker(speaker_address, msg, False)

            self.increment_invoked()
        except:
            self.logger.error(traceback.format_exc())
            self.increment_errors()
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")
    
    
    def _send_to_speaker(self, speaker_address, msg, play_announcement):
        '''
        Send the message to a specific speaker
        @param speaker_address address to speaker
        @param msg, voice message 
        @param play_announcement, determine if an announcement message should be played 
        before the actual message.
        '''
 #       if play_announcement == "True":
 #           commands.replace_queue(speaker_address, self.config['MESSAGE_ANNOUNCEMENT'])
 #           commands.append_tracks_in_queue(speaker_address, msg)
 #       else:
        commands.get_zone_group_state(speaker_address, msg)
#            commands.replace_queue(speaker_address, msg)
#        commands.send_play_with_index(speaker_address)
#        commands.set_play_mode(speaker_address)
        
    def get_speakers_from_config(self):
        '''
        Parse all configured speakers
        '''
        configuration = self.config['SONOS_SPEAKERS']
        for speaker_item in configuration:
            items = speaker_item.split(",")          
            self.speakers[items[0].strip()] = \
                SonosSpeaker(items[0].strip(), # Id,
                               items[1].strip(), #Slogan
                               items[2].strip(), # Address
                               items[3].strip(), # default speaker
                               items[4].strip() )# Play announcement

if __name__ == '__main__':

    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = SonosService()
    test.start("tts=skalskyddet_aktiverat")
