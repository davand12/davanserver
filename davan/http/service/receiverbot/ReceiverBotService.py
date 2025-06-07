'''
@author: davandev
'''
# coding: utf-8
import logging
import os
import traceback
import json
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.keyboardbutton import KeyboardButton


import urllib.request, urllib.parse, urllib.error
import re

from threading import Thread,Event
import davan.config.config_creator as configuration
import davan.util.constants as constants
import davan.util.helper_functions as helper_functions
import davan.util.converter_functions as converter
from davan.util import application_logger as log_manager
from davan.http.service.base_service import BaseService

logger = logging.getLogger(os.path.basename(__file__))

COMMAND, SPEAKER, TTS, SERVICES, TV, TVTEXT, LOG , SERVICESTATUS= list(range(8))

class ReceiverBotService(BaseService):
    '''
    Start a telegram bot to handle 
    Requires python-telegram-bot:
    pip install python-telegram-bot
    '''

    def __init__(self, service_provider, config):
        '''
        Constructor
        '''
        BaseService.__init__(self,constants.RECEIVER_BOT_SERVICE_NAME, service_provider, config)
        self.logger = logging.getLogger(os.path.basename(__file__))
        #logging.getLogger('telegram.bot').setLevel(logging.CRITICAL)
        #logging.getLogger('telegram.ext').setLevel(logging.CRITICAL)        
        #logging.getLogger('telegram.vendor').setLevel(logging.CRITICAL)
        self.current_speaker = "0"
        self.selected_service = None
        self.TAG_RE = re.compile(r'<[^>]+>')
        self.event = Event()
        self.bot = None
        self.handler = None

    def _parse_request(self,msg):
        self.logger.info("Parse request:" + msg)
        return msg.replace("/ReceiverBotService3=", "")
                
    def handle_request(self, msg):
        '''
        Received http request
        '''
        command = self._parse_request(msg)
        
        if command == "stop":
            self.stop_service()
        
        if command == "start":
            self.start_service()
        return constants.RESPONSE_OK, constants.MIME_TYPE_HTML, constants.RESPONSE_EMPTY_MSG.encode("utf-8")
    
    def tts(self, update, context):
        text = str(update.message.text.replace("/tts ", ""))
        tts_service = self.services.get_service(constants.TTS_SERVICE_NAME)
        tts_service.start(text, self.current_speaker)
        self.increment_invoked()
        update.message.reply_text("Text message played in speaker "+ str(self.current_speaker))
        self.build_start_menu(update, None)
        return COMMAND


    def tv(self, update, context):
        text = str(update.message.text.replace("/tv ", ""))
        encoded_message = helper_functions.encode_message(text.encode('utf-8'))
        url = 'http://192.168.2.173:80/web/message?text=%s&type=1&timeout=5' %encoded_message
        result = urllib.request.urlopen(url)
        res = result.read()
        self.increment_invoked()
        update.message.reply_text("Text message displayed on tv")
        self.build_tv_menu(update)
        return TV
        
#     def log(self, bot, update):
#         file_name = log_manager.get_logfile_name()
#         self.increment_invoked()
#         bot.send_document(chat_id=update.message.chat_id, document=open(file_name, 'r'))
#         return "Logfile sent"

    def audio(self, update, context):
        '''
        Recieved a voice message, play it in speakers 
        '''
        bot = context.bot
        self.handle_voice_message(bot, update.message)
        self.increment_invoked()
        update.message.reply_text('Voice message played in speaker ' +str(self.current_speaker))

    def stop_service(self):
        '''
        Stop telegram-bot 
        '''
        self.logger.info("Stopping service")
        try:
            self.bot.stop()
            self.event.set()
        except Exception:
            logger.error(traceback.format_exc())
#             
    def start_service(self):
        '''
        Start a telegram-bot and register command and message handlers.
        '''
        self.logger.info("Starting telegram conversation bot")
        self.bot = Updater(token=self.config["RECEIVER_BOT_TOKEN"],use_context=True)
        self.bot.dispatcher.add_handler(MessageHandler(Filters.voice, self.audio))
        # Get the dispatcher to register handlers
        dp = self.bot.dispatcher
     
        # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('c', self.build_start_menu)],
     
            states={
                COMMAND: [MessageHandler(Filters.regex('^(Services|Log|Speakers|TTS|Tv|Status)$'), self.handle_command)],
                SPEAKER: [MessageHandler(Filters.regex('^(Hallway|Kitchen|All|Menu)$'), self.handle_speaker)],
                SERVICES: [MessageHandler(Filters.regex('^(.*)$'), self.handle_service)],
                SERVICESTATUS: [MessageHandler(Filters.regex('^(Status|Enable|Disable|Services)$'), self.handle_service_status)],
                TV: [MessageHandler(Filters.regex('^(On|Off|Text|Menu)$'), self.handle_tv)],
                TTS: [MessageHandler(Filters.text, self.tts)],
                LOG: [MessageHandler(Filters.regex('^(INFO|DEBUG|Logfile|Keypad log|Menu)$'), self.handle_log)],
                TVTEXT: [MessageHandler(Filters.text, self.tv)]
            },
     
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
     
        dp.add_handler(conv_handler)
     
 
        def loop():
            self.bot.start_polling()
         
        Thread(target=loop).start()    
        self.is_running = True
        return self.event.set

            
    def handle_voice_message(self, bot, message):
        '''
        A voice message is returned from Telegram, download it.
        Convert the downloaded ogg file to wav, needed since the 
        roxcore speakers cannot handle the ogg encoding.
        @param message message to play in speaker.
        '''
        ogg_file = self.config['TEMP_PATH'] + 'telegram_voice.ogg'
        file_id = message.voice.file_id
        newFile = bot.get_file(file_id)
        newFile.download(ogg_file)        
        wav_file = converter.ogg_to_wav(self.config, ogg_file)
        speaker = self.services.get_service(constants.VOLUMIO_SERVICE_NAME)
        speaker.handle_request(wav_file,self.current_speaker)
        return "Voice message played in speaker " + str(self.current_speaker)
    
    def build_start_menu(self, update, context):
        '''
        Generate the start/command menu to display
        '''
        reply_keyboard = [['Status','Services', 'Log'],['TTS','Tv','Speakers']]
        
        update.message.reply_text("Select command:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
 
        return COMMAND
 
    def build_speaker_menu(self,update,context):
        '''
        Generate the speaker menu to display
        '''
        reply_keyboard = [['Hallway', 'Kitchen', 'All'],['Menu']]
        
        update.message.reply_text('Select speaker:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

    def build_tv_menu(self,update,context):
        '''
        Generate the tv menu to display
        '''
        reply_keyboard = [['On', 'Off', 'Text'],['Menu']]
        
        update.message.reply_text('Select command:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

    def build_log_menu(self,update, context):
        '''
        Generate the log menu to display
        '''
        reply_keyboard = [['INFO', 'DEBUG', 'Logfile'],['Keypad log','Menu']]
        
        update.message.reply_text('Select command:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

    def build_service_menu(self, update,context):
        '''
        Generate the service menu to display
        '''
        button_list = []
        for name, service in self.services.services.items():
            if service.is_enabled():
                button_list.append(KeyboardButton(name))
            
        footer = [KeyboardButton("Menu")]
        reply_keyboard = self.build_menu(button_list, 3, None, footer_buttons=footer)
        update.message.reply_text(
        'Select service:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
 
    def handle_command(self, update, context):
        '''
        Command has been selected, perform action
        '''
        logger.info("Selected command [%s]" % (update.message.text))
        
        if update.message.text == "Speakers":
            self.build_speaker_menu(update,context)
            return SPEAKER
        
        if update.message.text == "Status":
            self.handle_status(update,context)
            return COMMAND
        
        if update.message.text == "Log":
            self.build_log_menu(update,context)
            return LOG
        
        if update.message.text == "TTS":
            self.handle_tts(update,context)
            return TTS    
        
        if update.message.text == "Tv":
            self.build_tv_menu(update,context)
            #self.handle_tv(bot, update)
            return TV
        
        if update.message.text == "Services":
            self.build_service_menu(update,context)
            return SERVICES    
            
        return ConversationHandler.END    

    def handle_service(self, update, context):
        logger.info("Selected service [%s]" % (update.message.text))
        
        self.selected_service = update.message.text
        
        if update.message.text == "Menu":
            self.build_start_menu(update, context)
            return COMMAND

        self.build_service_control_menu(update, context)
        return SERVICESTATUS

    def handle_service_status(self,update,context):
        
        logger.info("Status of service [%s]" % (self.selected_service))
        if update.message.text == "Status":
            for name, service in self.services.services.items():
                if name == self.selected_service:
                    item = self.services.get_service(name)
                    text = item.get_html_gui("")   
                    success, error = item.get_counters()
                    result = text + "\n" + "Success: " + str(success) + "\nError:" + str(error)
                    result += "\nEnabled[" + str(item.is_service_running()) + "]"
                    result += "\nLastTimeout[" + str(item.get_last_timeout()) + "]"
                    result += "\nNextTimeout[" + str(item.get_next_timeout()) + "]"
                    self.increment_invoked()
    #                update.message.reply_text(self.TAG_RE.sub('', text),reply_markup=ReplyKeyboardRemove())
                    update.message.reply_text(self.TAG_RE.sub('', result))
            return SERVICESTATUS    
        elif update.message.text == "Enable":
            logger.info("Enable service")
            item = self.services.services[self.selected_service]
            item.start_service()
            result = self.selected_service +" enabled ["+str(item.is_service_running())+"]"
            update.message.reply_text(self.TAG_RE.sub('', result))
            return SERVICESTATUS    
        elif update.message.text == "Disable":
            logger.info("Disable service")
            item = self.services.services[self.selected_service]
            item.stop_service()
            result = self.selected_service +" enabled ["+str(item.is_service_running())+"]"
            update.message.reply_text(result)
            return SERVICESTATUS    
        elif update.message.text == "Services":
            logger.info("Services service")
            self.build_service_menu(update,context)
            return SERVICES    
        
    def build_service_control_menu(self, update, context):
        '''
        Generate the start/command menu to display
        '''
        reply_keyboard = [['Status','Enable', 'Disable'],['Services']]
        
        update.message.reply_text("Select command:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
 
        return COMMAND

    def handle_status(self, update, context):
        logger.info("Selected [%s]" % (update.message.text))
        service = self.services.get_service(constants.HTML_SERVICE_NAME)
        result = json.loads(service.get_status())
        res_string = "Uptime: " + str(result['Uptime']) +"\n"
        res_string += "Server started: " + str(result['ServerStarted']) +"\n"
        res_string += "Cpu load: " + str(result['CpuLoad']) +"\n"
        res_string += "Disk usage : " + str(result['Disk']) +"\n"
        res_string += "Memory usage (used/free): " + str(result['Memory']) +"\n"
        
        res_string += "Services: " + str(result['Services'])
        update.message.reply_text(self.TAG_RE.sub('', res_string))
        self.build_start_menu(update, context)
        return COMMAND

    def handle_tts(self, update, context):
        '''
        '''
        logger.info("Selected tts [%s]" % (update.message.text))
        update.message.reply_text("Write message to play in speaker ", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def handle_log(self, update, context):
        '''
        Handle the selected log command
        '''
        logger.info("Selected log-command [%s]" % (update.message.text))
        if update.message.text != 'Menu':
            if update.message.text == 'INFO':
                update.message.reply_text("Changing loglevel to INFO")
                log_manager.change_loglevel(3)
                return LOG 
            if update.message.text == 'DEBUG':
                update.message.reply_text("Changing loglevel to DEBUG")
                log_manager.change_loglevel(4)
                return LOG 
            if update.message.text == 'Logfile':
                file_name = log_manager.get_logfile_name()
                context.bot.send_document(chat_id=update.message.chat_id, document=open(file_name, 'rb'))
                return LOG 
            if update.message.text == 'Keypad log':
                keypad_service = self.services.get_service(constants.KEYPAD_SERVICE_NAME)
                log_file = keypad_service.get_log()
                self.bot.send_document(chat_id=update.message.chat_id, document=open(log_file, 'rb'))
                return LOG 

            self.increment_invoked()
        self.build_start_menu(update, context)
        return COMMAND

    def handle_tv(self, update, context):
        '''
        Handle the selected tv command
        '''
        logger.info("Selected tv-command [%s]" % (update.message.text))
        if update.message.text != 'Menu':
            if update.message.text == 'On':
                update.message.reply_text("Turning on TV")
                tv = self.services.get_service("TvService")
                tv.enable(True)
                update.message.reply_text("Turned on TV ")
                return TV    
            if update.message.text == 'Off':
                update.message.reply_text("Turning off TV")
                tv = self.services.get_service("TvService")
                tv.enable(False)
                update.message.reply_text("Turned off TV")
                return TV
            if update.message.text == 'Text':
                update.message.reply_text("Write message on TV", reply_markup=ReplyKeyboardRemove())
                #self.handle_show_text(bot,update)
                return TVTEXT 

            self.increment_invoked()
        self.build_start_menu(update, None)
        return COMMAND


    def handle_speaker(self, update, context):
        '''
        A speaker has been selected
        '''
        logger.info("Selected speaker %s:" % (update.message.text))
        if update.message.text != 'Menu':
            if update.message.text == 'Kitchen':
                self.current_speaker = "0"
            if update.message.text == 'Hallway':
                self.current_speaker = "1"
            if update.message.text == 'All':
                self.current_speaker = "2"

            self.increment_invoked()
            update.message.reply_text("Current speaker is now: " + update.message.text)
        self.build_start_menu(update,context)
        return COMMAND
 
    def cancel(self, update, context):
        logger.info("User canceled the conversation.")
 
        return ConversationHandler.END    
    
    def build_menu(self, buttons,
                   n_cols,
                   header_buttons=None,
                   footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)
        return menu                

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
        column = column.replace("<SERVICE_VALUE>", "<li>Monitor: " + str() + " </li>\n")
        return column


if __name__ == '__main__':
    config = configuration.create()
    log_manager.start_logging(config['LOGFILE_PATH'],loglevel=4)
    test = ReceiverBotService(None, config)
    test.start_service()
