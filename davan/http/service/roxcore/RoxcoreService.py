'''
Created on 17 feb. 2017

@author: davandev
'''

import logging
import os
import re
import traceback
from davan.http.service.base_service import BaseService
from davan.util import application_logger as app_logger
import davan.util.constants as constants
import davan.util.helper_functions as helper
import davan.config.config_creator as configuration
import davan.http.service.roxcore.RoxcoreSpeakerCommands as commands

class RoxcoreSpeaker():
    def __init__(self, id, slogan, address, default_speaker, play_announcement):
        self.logger = logging.getLogger(os.path.basename(__file__))

        self.id = id 
        self.slogan = slogan
        self.address = address
        self.default_speaker = default_speaker
        self.play_announcement = play_announcement


    def toString(self):
        return "Slogan[ "+self.slogan+" ] "\
            "Id[ "+self.id+" ] "\
            "Address[ "+self.address+" ] "\
            "Speaker[ "+self.default_speaker+" ] "\
            "Announcement[ "+self.play_announcement+" ]"

class RoxcoreService(BaseService):
    '''
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self, constants.ROXCORE_SPEAKER_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.state_exp = re.compile(r'<CurrentTransportState>(.+?)<\/CurrentTransportState>')
        self.uri_exp = re.compile(r'<TrackURI>(.+?)<\/TrackURI>')
        self.speakers = {}

    def init_service(self):
        self.get_speakers_from_config()

    def do_self_test(self):
        pass

    def handle_request(self, msg, speaker_id="0"):
        '''
        Play mp3 file on Roxcore speaker.
        @param msg, file to play 
        '''
        try:
            self.logger.info("Play in speaker[" + self.speakers[speaker_id].slogan+"]")
            if speaker_id == "2":
                for _,speaker in list(self.speakers.items()):
                    self.logger.info("Play in:" + speaker.slogan)
                    speaker_address = "http://" + speaker.address + ":" + self.config['ROXCORE_PORT_NR']
                    self._send_to_speaker(speaker_address, msg, speaker.play_announcement)
            else:
                speaker_address = "http://" + self.speakers[speaker_id].address + ":" + self.config['ROXCORE_PORT_NR']
                self.logger.info(self.speakers[speaker_id].toString())
                self._send_to_speaker(speaker_address, msg, self.speakers[speaker_id].play_announcement)
            self.increment_invoked()
        except:
            msg = "Misslyckades att spela upp meddelande i högtalare ["+ self.speakers[speaker_id].slogan+"]"
            helper.send_telegram_message(self.config, msg)
            self.raise_alarm(constants.ROXCORE_SPEAKER_SERVICE_NAME, "Warning", msg)
            
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
        try:
            current_play = self.maybe_save_current_play(speaker_address)
        except:
            self.logger.info("Failed to determine current played stream")
            current_play = None
            
        if play_announcement == "True":
            commands.replace_queue(speaker_address, self.config['MESSAGE_ANNOUNCEMENT'])
            commands.append_tracks_in_queue(speaker_address, msg)
        else:
            commands.replace_queue(speaker_address, msg)

        if current_play != None:
            commands.append_external_tracks_in_queue(speaker_address, current_play)

        commands.send_play_with_index(speaker_address)
        commands.set_play_mode(speaker_address)

    def stop_playing(self):
        for _,speaker in list(self.speakers.items()):
            self.logger.info("Stop playing in speaker: " + speaker.slogan)
            speaker_address = "http://" + speaker.address + ":" + self.config['ROXCORE_PORT_NR']
            commands.stop(speaker_address)
        
    def play_external_url(self, url):
            speaker_address = "http://" + self.speakers["0"].address + ":" + self.config['ROXCORE_PORT_NR']
            self.logger.info("Start playing url : " + url)
            commands.append_external_tracks_in_queue(speaker_address, url)
            commands.send_play_with_index(speaker_address)
            commands.set_play_mode(speaker_address)
            
    def maybe_save_current_play(self,speaker_address):
        result = commands.get_info(speaker_address)
        current_uri = None
        
        match = self.state_exp.search(str(result.text))
        if match:
            current_state = match.group(1).strip()
            self.logger.debug(str(current_state))
            if "STOPPED" in current_state:
                self.logger.debug("Nothing is currently playing.")
            elif "PLAYING" in current_state:
                match = self.uri_exp.search(str(result.text))
                if match:
                    current_uri = match.group(1).strip()
                    self.logger.debug("currently playing "+current_uri)
        self.logger.debug(str(result.text))
        return current_uri

    def has_html_gui(self):
        """
        Override if service has gui
        """
        return True
    
    def get_html_gui(self, column_id):
        """
        Override and provide gui
        """
        if not self.is_enabled():
            return BaseService.get_html_gui(self, column_id)

        column = constants.COLUMN_TAG.replace("<COLUMN_ID>", str(column_id))
        column = column.replace("<SERVICE_NAME>", self.service_name)
        res = "Speakers:\n"
        for _,speaker in list(self.speakers.items()):
            res += speaker.slogan + ":" + speaker.address + "\n"
        column  = column.replace("<SERVICE_VALUE>", res)

        return column
    
    def get_speakers_from_config(self):
        '''
        Parse all configured speakers
        '''
        configuration = self.config['ROXCORE_SPEAKERS']
        for speaker_item in configuration:
            items = speaker_item.split(",")          
            self.speakers[items[0].strip()] = \
                RoxcoreSpeaker(items[0].strip(), # Id,
                               items[1].strip(), #Slogan
                               items[2].strip(), # Address
                               items[3].strip(), # default speaker
                               items[4].strip() )# Play announcement
        
        
if __name__ == '__main__':

    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = RoxcoreService("",config)
    test.handle_request("telegram_voice.mp3")
