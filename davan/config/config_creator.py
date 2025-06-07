"""
Creates the config data used by services.

@author: Davandev
"""

import davan.util.helper_functions as common
import os
import imp

def create_config(secret_config, config):

    #------------------------------------------------------------------------------------------------
    # General server configuration
    #------------------------------------------------------------------------------------------------
    # CRITICAL=0, ERROR,WARNING,INFO,DEBUG=4
    config["LOGLEVEL"]      = 3
    # Root path of server
    config["ROOT"]          = '/home/pi/davanserver/'
    # Log directory path
    config['LOGFILE_PATH']  = config["ROOT"] + "logs"
    config['TEMP_PATH']     = config["ROOT"] + "temp"
    # Service directory path
    config['SERVICE_PATH']  = config["ROOT"] + "davan/http/service/"
    # Server port
    config["SERVER_PORT"]   = 8080
    config["SERVER_ADRESS"] = "192.168.50.43"

    #---------------------------------------------------------------------------------------------
    # Fibaro configuration
    #---------------------------------------------------------------------------------------------
    config['FIBARO_USER_NAME']   = secret_config.FIBARO_USER
    config['FIBARO_PASSWORD']    = secret_config.FIBARO_PASSWORD
    config['FIBARO_IP_ADDRESS']  = "192.168.50.174"

    #---------------------------------------------------------------------------------------------
    # Fibaro path for common functions
    # --------------------------------------------------------------------------------------------
    # Fibaro api access path
    #config['FIBARO_API_ADDRESS'] = "http://" + config['FIBARO_USER_NAME'] + ":" + config['FIBARO_PASSWORD'] + "@" + config['FIBARO_IP_ADDRESS'] + "/api/"
    config['FIBARO_API_ADDRESS'] = "http://" + config['FIBARO_IP_ADDRESS'] + "/api/"
    # Set property in a virtual device
    config['UPDATE_DEVICE'] = config['FIBARO_API_ADDRESS'] + "callAction?deviceID=<DEVICEID>&name=setProperty&arg1=<LABELID>&arg2=<VALUE>"
    # Press button on virtual device
    config['VD_PRESS_BUTTON_URL'] =  config['FIBARO_API_ADDRESS'] + "callAction?deviceID=<ID>&name=pressButton&arg1=<BUTTONID>"
    # Get state of a scene
    config['GET_STATE_SCENE_URL'] = config['FIBARO_API_ADDRESS'] + "scenes/<ID>"
    # Command to start a scene
    config['START_SCENE_URL'] = config['FIBARO_API_ADDRESS'] + "sceneControl?id=<ID>&action=start"
    # Command to set a value on a device (dimmer)
    config['DEVICE_SET_VALUE_WITH_ARG_URL'] =  config['FIBARO_API_ADDRESS'] + "callAction?deviceID=<ID>&name=setValue&arg1=<VALUE>"
    config['DEVICE_SET_VALUE_URL'] =  config['FIBARO_API_ADDRESS'] + "callAction?deviceID=<ID>&name=<VALUE>"


    #-----------------------------------------------------------------------------------------
    # Logreceiver configuration
    #-----------------------------------------------------------------------------------------
    config["LogEntryEnabled"] = True

    # Log directory path
    config['HC2LOG_PATH'] = config["LOGFILE_PATH"] + "/hc2"
    
    #---------------------------------------------------------------------------------------------
    # Telegram configuration
    #---------------------------------------------------------------------------------------------
    # Telegram chat id, stored in a dict 
    config['CHATID'] = secret_config.TELEGRAM_CHATID
    # Telegram token
    config['TOKEN'] = secret_config.TELEGRAM_TOKEN
    # Telegram api path for sending messages
    config['TELEGRAM_PATH'] = "https://api.telegram.org/bot"+config['TOKEN']+"/sendMessage?chat_id=<CHATID>&text="
    
    #---------------------------------------------------------------------------------------------    
    # Outdoor camera configuration
    #---------------------------------------------------------------------------------------------
    config["TakePictureEnabled"] = True
    config['CAMERAS'] = {'Balkong':'http://192.168.2.193:99/snapshot.cgi/snapshot.cgi',
                         'Uterum':'http://192.168.2.77:99/snapshot.cgi/snapshot.cgi',
                         'Farstukvist':'http://192.168.2.172/tmpfs/snap.jpg',
                         'Dlink2':'http://192.168.2.117/image/jpeg.cgi'}
    # Username used when accessing cameras
    config['CAMERA_USER'] = secret_config.CAMERA_USER
    # Password used when accessing cameras
    config['CAMERA_PASSWORD'] = secret_config.CAMERA_PASSWORD
    
    #---------------------------------------------------------------------------------------
    # Presence Service configuration
    #---------------------------------------------------------------------------------------
    config["presenceEnabled"] = False
    # Scene ids for each user
    config['MIA_AWAY_SCENE_ID'] = "13"
    config['MIA_HOME_SCENE_ID'] = "12"
    config['DAVID_AWAY_SCENE_ID'] = "10"
    config['DAVID_HOME_SCENE_ID'] = "9"
    config['WILMA_AWAY_SCENE_ID'] = "15"
    config['WILMA_HOME_SCENE_ID'] = "14"
    config['VIGGO_HOME_SCENE_ID'] = "16"
    config['VIGGO_AWAY_SCENE_ID'] = "17"

    #---------------------------------------------------------------------------------------
    # Asus router presence Service configuration
    #---------------------------------------------------------------------------------------
    config["DevicePresenceServiceEnabled"] = False
    config["ROUTER_ADRESS"] = "192.168.50.1"
    config["ROUTER_USER"] = secret_config.ROUTER_USER
    config["ROUTER_PASSWORD"] = secret_config.ROUTER_PASSWORD
    # Virtual device id of the virtual device in HC2 that shows the presence of the users 
    config['FIBARO_VD_PRESENCE_ID'] = "75"
    # Mappings of users and the label in the presense virtual device
    config['FIBARO_VD_MAPPINGS'] = {
      # User    : HC2 Virtualdevice ID
        'Wilma' : 'ui.Label3.value',
        'David' : 'ui.Label1.value',
          'Mia' : 'ui.Label2.value',
        'Viggo' : 'ui.Label4.value' }

    # Ipadresses of devices where its wifi presence should be monitored
    config['FAMILY_DEVICES'] = secret_config.DEVICES_FAMILY
    config['GUEST_DEVICES'] = secret_config.DEVICES_FRIEND
    config['HOUSE_DEVICES'] = secret_config.DEVICES_HOUSE
    config['UNKNOWN_DEVICES'] = secret_config.DEVICES_UNKNOWN
#---------------------------------------------------------------------------------------
    # Authentication configuration  98:00:c6:32:85:30
    #---------------------------------------------------------------------------------------
    config["authenticateEnabled"] = False

    config['disarmAlarm'] = config['FIBARO_API_ADDRESS'] + "sceneControl?id=36&action=start"
    config['disarmSkalskydd'] = config['FIBARO_API_ADDRESS'] + "sceneControl?id=38&action=start"
    config['armSkalskydd'] = config['FIBARO_API_ADDRESS'] + "sceneControl?id=34&action=start"
    config['armAlarm'] = config['FIBARO_API_ADDRESS'] + "sceneControl?id=35&action=start"
    
    # User pin codes    
    config['USER_PIN'] = secret_config.USER_PIN

    #---------------------------------------------------------------------------------------------
    # Telldus sensor configuration
    #---------------------------------------------------------------------------------------------
    config["TelldusSensorServiceEnabled"] = False
    config["telldusEnabled"] = False
    # Telldus public key
    config["TELLDUS_PUBLIC_KEY"] = secret_config.TELLDUS_PUBLIC_KEY
    # Telldus private key
    config["TELLDUS_PRIVATE_KEY"] =  secret_config.TELLDUS_PRIVATE_KEY
    config["TELLDUS_TOKEN"] =  secret_config.TELLDUS_TOKEN
    config["TELLDUS_TOKEN_SECRET"] =  secret_config.TELLDUS_TOKEN_SECRET
    
    # Dict holding name of room and virtual device id
    config['SENSOR_MAP'] = {
               # Room name : HC2 Virtualdevice ID 
                  'Badrum' :  '147', 
               'Tvattstuga':  '220',
                   'Garage':  '149',
               'Gillestuga':  '153',
              'Farstukvist':  '152',
                   'Sovrum':  '151',
                    'Wilma':  '150' }
    
    config['SENSOR_HUMIDITY_LIMITS'] = {'Badrum': 60, 'Tvattstuga': 60}
    config['SENSOR_TEMP_HIGH_LIMITS'] = {}
    config['SENSOR_TEMP_LOW_LIMITS'] = {}
    # Temperature virtual devices 
    config['LABEL_TEMP'] = "ui.Label1.value"
    config['LABEL_HUMIDITY'] = "ui.Label2.value"
    config['LABEL_DATE'] = "ui.Label3.value"

    #---------------------------------------------------------------------------------------------
    # Keypad keep alive configuration   
    #---------------------------------------------------------------------------------------------
    config["KeypadAliveServiceEnabled"] = False
    # IP address of android alarm keypad
    config['KEYPAD_IP_ADDRESSES'] = {
               # Name :  IP Address 
                  'S4'  :  '192.168.2.155:8080'}
                  #'S6'  :  '192.168.2.88:8080',  
                  #'P5'  :  '192.168.2.233:8080', 
                  #'lgg4':  '192.168.2.100:8080'}
    
    config['KEYPAD_IP_ADDRESS']         = "192.168.2.155:8080"
    
    config["KEYPAD_LOG_FILE"]           = config['TEMP_PATH'] + "/keypad_log.txt"
    # URI used to verify if keypad is alive
    config['KEYPAD_PING_URL']           = "http://%IP%/Ping"
    # URI used to fetch logfile
    config['KEYPAD_LOG_URL']            = "http://" + config['KEYPAD_IP_ADDRESS'] + "/log"
    #-----------------------------------------------------------------------------------------
    # TTS configuration
    #-----------------------------------------------------------------------------------------
    config["ttsEnabled"] = True
    # VoiceRSS token
    config['VOICERSS_TOKEN'] = secret_config.VOICERSS_TOKEN
    # VoiceRSS api path for generating mp3 from message 
    config['VOICERSS_URL'] = "http://api.voicerss.org/?key=" + config['VOICERSS_TOKEN'] + "&src=REPLACE_WITH_MESSAGE&f=22khz_16bit_mono&hl=sv-se"
    # Url with key where to translate message to mp3
    config['TTS_GENERATOR_IP_ADDRESS'] = "192.168.2.155:8080"
    # Path to cached tts messages
    config['TTS_PRECOMPILED_MSG_PATH'] = config["ROOT"] + "davan/tts_mp3/"
    # Path to cached tts alarm messages
    config['TTS_PRECOMPILED_ALARM_MSG_PATH'] = config["TTS_PRECOMPILED_MSG_PATH"] + "alarm/"
    # Mp3 file to play
    config['SPEAK_FILE'] = '/dev/shm/speak.mp3'
    # Application used to play mp3 file on raspberry pi
    config['SPEAK_CMD'] = '/usr/bin/mpg123'
    # Url to fetch created mp3 file on android phone
    config['TTS_GENERATOR_FETCH_URL'] = "http://" + config['TTS_GENERATOR_IP_ADDRESS'] + "/ttsFetch"
    # Url to generate mp3 file on android phone
    config['TTS_GENERATOR_CREATE_URL'] = "http://" + config['TTS_GENERATOR_IP_ADDRESS'] + "/tts"
    # Select the speakers for plauging TTS messages, currently supports 
    # "RoxcoreService", "SonosService" or internal speaker
    #config['SPEAKER_SERVICE'] = "RoxcoreService"
    config['SPEAKER_SERVICE'] = "VolumioService"
    config['SPEAKER_SERVICES'] = {"1":"VolumioService","2":"RoxcoreService"}
    #-----------------------------------------------------------------------------------------
    # Mp3 provider configuration
    #-----------------------------------------------------------------------------------------
    config["mp3Enabled"] = True
    config['MP3_ROOT_FOLDER'] = config['TTS_PRECOMPILED_MSG_PATH']
 
    
    #-----------------------------------------------------------------------------------------
    # DailyQuote configuration
    #-----------------------------------------------------------------------------------------
    config["DailyQuoteEnabled"] = True
    # Path to dailyquote path
    config['TTS_DAILY_QUOTE_PATH'] = config["TTS_PRECOMPILED_MSG_PATH"] + "daily_quote/"
    # Path to dailyquote file
    config['TTS_DAILY_QUOTE_FILE'] = config['TTS_DAILY_QUOTE_PATH'] + "daily_quote.mp3"
    
    
    #---------------------------------------------------------------------------------------------
    # Scenes to monitor, start if not running
    # Monitors running scens on fibaro system
    #---------------------------------------------------------------------------------------------
    config["ActiveScenesMonitorEnabled"] = True
    # List of scenes that should be monitored
    config['MONITOR_SCENES'] = {'32'} # Clock scene
    
    #---------------------------------------------------------------------------------------------
    # UPS Virtual device configuration
    #---------------------------------------------------------------------------------------------
    config["UpsEnabled"] = True
    # UPS virtual id on fibaro system
    config["UPS_VD_ID"] = "156"
    # 
    config["UPS_BUTTON_ID"] = "6"

    #---------------------------------------------------------------------------------------------
    # Internet speed test configuration
    #---------------------------------------------------------------------------------------------
    config["SpeedtestServiceEnabled"]  = True
    config['FIBARO_VD_SPEEDTEST'] = "77"

    config['FIBARO_VD_SPEEDTEST_MAPPINGS'] = {
      # User    : HC2 Virtualdevice ID
        'Ping'     : 'ui.ping.value',
        'Download' : 'ui.download.value',
        'Upload'   : 'ui.upload.value',
        'Status'   : 'ui.status.value',
        'Time'     : 'ui.time.value'
}

    #---------------------------------------------------------------------------------------------
    # Audio service configuration
    #---------------------------------------------------------------------------------------------
    config["AudioServiceEnabled"]   = False
    config['RECEIVER_TURN_ON']      = "onkyo --host 192.168.2.218 PWR01"
    config['RECEIVER_TURN_OFF']     = "onkyo --host 192.168.2.218 PWR00"
    config['RECEIVER_SELECT_INPUT'] = "onkyo --host 192.168.2.218 SLI02"
    config['RECEIVER_SET_VOLUME']   = "onkyo --host 192.168.2.218 MVL25"
    config["CHROMECAST_NAME"]       = "ChromecastEntre"

    #---------------------------------------------------------------------------------------------
    # HTML Service configuration
    #---------------------------------------------------------------------------------------------
    config["HtmlServiceEnabled"] = True
    config["HTML_INDEX_FILE"] = config['SERVICE_PATH'] + "html/index_template.html"
    config["HTML_STYLE_FILE"] = config['SERVICE_PATH'] + "html/style.css"
    config["HTML_STATISTICS_FILE"]  = config['SERVICE_PATH'] + "html/statistics_template.html"
    config["HTML_SELECT_LOGFILE"] = config['SERVICE_PATH'] + "html/select_logfile.html"

    #---------------------------------------------------------------------------------------------
    # Sonos Service configuration
    #---------------------------------------------------------------------------------------------
    config["SonosServiceEnabled"] = False
    # Adress to Sonos speaker
    config['SONOS_SPEAKERS'] = [
        #Id,    |  Slogan       | Address     |  Default  | Play Announcement msg                         
        '0,        Livingroom,   192.168.2.108,  True,         False',
        '1,        Hallway,      192.168.2.108,  False,        False',
        '2,         All,         ,               False,        True',
    
    ]
    #---------------------------------------------------------------------------------------------
    # Weather Service configuration
    #---------------------------------------------------------------------------------------------
    config["WeatherEnabled"]     = True
    config["WEATHER_API_PATH"]   = "https://api.weather.com/v2/pws/observations/current?stationId=<STATIONID>&format=json&units=m&apiKey=<API_KEY>&numericPrecision=decimal"
    config["WEATHER_FORECAST_PATH"] = "https://api.weather.com/v3/wx/forecast/daily/5day?geocode=<GEO_CODE>&format=json&units=s&language=sv-SE&apiKey=<API_KEY>"
    config["WEATHER_TOKEN"]      = secret_config.WEATHER_TOKEN
    config["WEATHER_GEOCODE"]    = secret_config.WEATHER_GEOCODE
    config["WEATHER_STATION_ID"] = secret_config.WEATHER_STATION_ID
    
    # Weather virtual id on fibaro system
    config["WEATHER_VD_ID"] = "79"
    # Weather button to push
    config["WEATHER_BUTTON_ID"] = "7"


    #---------------------------------------------------------------------------------------------
    # LightSchema Service configuration
    # deviceType 0=Onoff, 1=dimmer, 2=virtualdevice, 3=serviceNotification
    # Room, StartTime, StopTime, Interval(week/weekdays/weekend), lightLevel(0-100), deviceId, buttonId, randomTime, virtualDeviceUpdateId
    #---------------------------------------------------------------------------------------------
    config["LightSchemaServiceEnabled"] = True 
    config['LIGHT_SCHEMA'] = [
        #Room               | start | stop | Interval | deviceType | lightlevel | deviceId | labelid | random | virtualdevice | Only when armed 
        #'KitchenTak,         06:15,   08:30, weekdays,     1,           10,        65,         1,        15,        194,            0',
        'Outdoor,             sunset,   23:20,  week,         0,           -1,        359,        1,        20,        196,            0',
        #'Bevattning,          21:00,  21:12,   week,        0,            2,        441,        2,        0,         196,            0',      
        'Poolpump,            10:00,  16:00,   week,        0,            2,        267,        3,        0,         196,            0',      
        'Poolpump,            02:00,  04:00,   week,        0,            2,        267,        4,        0,         196,            0',      
        #'RobomowSocket,        07:30,   21:00,  Tuesday,      0,           2,         267,        2,        0,         196,            0',
        #'PoolService,          01:00,   09:00,  week,         3,          -1,         267,        4,        0,         196,            0',      
        #'RobomowSocket,        07:30,   21:00,  Thursday,     0,           2,         267,        2,        0,         196,            0',
        #'RobomowSocket,        07:30,   21:00,  Saturday,     0,           2,         267,        2,        0,         196,            0',
        #'RobomowService,       07:30,   17:00,  Monday,       3,          -1,         13,        2,        0,         196,            0',
        'RobomowService,       07:00,   18:00,  Tuesday,      3,          -1,         13,        2,        0,         196,            0',
        'RobomowService,       07:00,   18:00,  Friday,       3,          -1,         13,        2,        0,         196,            0',
        #'ljusslinga,           07:00,   09:05,  weekdays,     2,           2,         179,        1,        3,         194,            0',
        #'ljusslinga,           18:00,   23:15,  week,         2,           2,         179,        2,        3,         194,            0',
        'ljusstakar,            06:00,   09:15,  weekdays,     2,           19,        179,        7,        3,         194,            0',
        'ljusstakar,            09:00,   23:55,  weekend,      2,           19,        179,        7,        3,         194,            0',

        'ljusstakar,           16:00,   23:45,  week,          2,           19,        179,        7,        3,         194,            0',
        #'KitchenGroup,         06:30,   08:30,  weekdays,     2,           11,        179,        1,        3,         194,            0',
        'KitchenGroup,         sunset,   23:55,  week,         2,           11,        179,        2,        3,         194,            0',
        #'KitchenGroup,         08:00,   23:55,  weekend,      2,           11,        179,        1,        3,         194,            0',
        #'KitchenTak,           06:50,   09:00,  weekdays,     1,           5,         65,         3,        1,         194,            0',
        'KitchenTak,           sunset,   23:15,  week,         1,           5,         65,         3,        1,         194,            0',
        'Vitrin,                06:15,   08:30,  weekdays,     2,           6,         179,        4,        3,         194,            0',
        'Vitrin,                17:15,   23:45,  week,         2,           6,         179,        4,        3,         194,            0',
        #'KitchenMatsal,        06:55,   09:01,  weekdays,     1,           5,         394,        7,        1,         194,            0',
        'KitchenMatsal,        sunset,   23:30,  week,         1,           5,         394,        5,        1,         194,            0',
        #'KitchenLampa,         06:45,   08:05,  weekdays,     1,           10,        397,        9,        1,         194,            0',
        'KitchenLampa,         sunset,   22:05,  week,         1,           10,        397,        6,        1,         194,            0',
        #'Uterum,               07:05,   08:15,  week,         0,           -1,        360,        1,        10,        195,            0',
        'Uterum,               sunset,   23:30,  week,         0,           -1,        360,        1,        10,        195,            0',
        'Farstukvist,          sunset,   23:30,  week,         0,           -1,        226,        1,        1,         227,            0',
        #'WilmaFonster,         06:30,   08:10,  week,         2,           10,        180,        1,        3,         197,            0',
        'WilmaFonster,         sunset,   22:15,  weekdays,     2,           10,        180,        2,        3,         197,            0',
        'WilmaFonster,         sunset,   23:15,  weekend,      2,           10,        180,        2,        3,         197,            0',
        'WilmaBlinds,          08:30,    22:45,  weekdays,     2,           18,        180,        3,        3,         197,            0',
        'WilmaBlinds,          10:00,    22:55,  week,         2,           18,        180,        3,        3,         197,            0',
        #'WilmaTak,            06:30,    08:15,  weekdays,     1,           20,        173,        4,        20,        197,            1',
        'WilmaTak,             sunset,   22:00,  week,         1,           20,        173,        5,        20,        197,            1',
        #'ViggoFonster,         06:30,   08:00,  weekdays,     2,           10,        181,        1,        3,         198,            0',
        'ViggoFonster,         sunset,   21:30,  weekdays,     2,           10,        181,        2,        3,         198,            0',
        'ViggoFonster,         sunset,   23:00,  weekend,      2,           10,        181,        2,        3,         198,            0',
        'ViggoBlinds,          07:30,    22:00,  weekdays,     2,           14,        181,        3,        3,         198,            0',
        'ViggoBlinds,          10:00,    22:30,  week,         2,           14,        181,        3,        3,         198,            0',
        #'ViggoTak,            06:30,    07:15,  weekdays,     1,           10,        177,        4,        15,        198,            1',
        'ViggoTak ,            sunset,   21:00,  week,         1,           10,        177,        5,        15,        198,            1',
        #'Parkering,            19:00,    23:10,  week,         0,            2,        441,        1,        1,         281,            0',
        #'Bevattning,          21:00,  21:12,   week,        0,            2,        441,        2,        0,         196,            0',      
        #'Datarum,              06:15,   12:30,  week,         2,            2,        182,        1,        0,         304,            0',        
        'Datarum,              15:00,   23:42,  week,         2,            2,        182,        2,        0,         304,            0',
        'Tvrum,                sunset,   23:30,  week,         2,            2,        184,        1,        5,         307,            0',
        'Gillestuga,           sunset,   23:30,  week,         2,            10,       339,        1,        5,         390,            0',
        'Tavla,                sunset,   23:45,  week,         2,            14,       339,        2,        4,         390,            0',
        #'Sovrum,               09:15,   10:30,  weekend,      2,            2,        185,        1,        5,         308,            0',
        'Sovrum,               06:30,    07:15,  weekdays,     2,            2,        185,        2,        5,         308,            0',
        'Sovrum,               sunset,   23:30,  week,         2,            2,        185,        2,        5,         308,            0',
        #'Hall,                 06:30,    09:00,  weekdays,     1,            5,        375,        1,        5,         402,            0',
        'Hall,                 sunset,   23:40,  week,         1,            5,        375,        2,        5,         402,            0',
        'Korridor,             sunset,   23:40,  week,         1,            5,        286,        3,        5,         402,            0',

   ]
    config['LABEL_SCHEDULE'] = "ui.Schedule<BID>.value"

    #---------------------------------------------------------------------------------------------
    # ReceiverBot configuration
    #---------------------------------------------------------------------------------------------
    config["ReceiverBotServiceEnabled"] = True
    config["RECEIVER_BOT_TOKEN"] = secret_config.RECEIVER_BOT_TOKEN

    #---------------------------------------------------------------------------------------------
    # Roxcore speaker configuration
    #---------------------------------------------------------------------------------------------
    config["RoxcoreServiceEnabled"] = True
    config['ROXCORE_PORT_NR'] = "59152"
    config['ROXCORE_SPEAKERS'] = [
        #Id,    |  Slogan       | Address     |  Default  | Play Announcement msg                         
        '2,        Hallway,      192.168.2.121, True,        False',
        #'0,        Kitchen,      192.168.2.49,  True,         True',
        #'2,         All,            ,           False,        True',
    ]
    config['MESSAGE_ANNOUNCEMENT'] = "announcement.mp3"
    #---------------------------------------------------------------------------------------------
    # Announcement service
    #---------------------------------------------------------------------------------------------
    config["AnnouncementsServiceEnabled"] = True
    config["ANNOUNCEMENT_MENU_PATH"] = config["ROOT"] + "menu.txt"
    config["ANNOUNCEMENT_THEMEDAY_PATH"] = config["ROOT"] + "tema_dagar.txt"
    config["ANNOUNCEMENT_IDIOM"] = config["ROOT"] + "idiomatisk.txt"
    config["ANNOUNCEMENT_FACT"] = config["ROOT"] + "funfact.txt"
    config['ANNOUNCEMENTS_SCHEMA'] = [
        #Slogan          | Time, | Interval | | announcementname | speaker id | Text
        'SleepTime,        23:02,   weekdays,       night,           0,          Mia',
        'Morning,          07:15,   weekdays,       morning,         0,          -',
        'MorningWeekend,   09:30,   weekend,        morning,         0,          -',
        'Afternoon,        18:15,   week,           afternoon,        0,          -',
        'WilmaBirthDay,    08:00,   02/06,          birthday,        0,          -',
        'ViggoBirthDay,    08:00,   20/06,          birthday,        0,          -',
        'MiaBirthDay,      08:00,   30/06,          birthday,        0,          -',
        'DavidBirthDay,    08:00,   08/07,          birthday,        0,          -',
        'RadioWeekdaysOn,  07:00,   weekdays,       radio,           0,          https://fm01-ice.stream.khz.se/fm01_mp3',
        'RadioWeekdaysOff, 09:30,   weekdays,       radio,           0,          stop',
#        'EveningWater,     22:00,   week,           water,           0',
   ]

    #---------------------------------------------------------------------------------------------
    # Calendar service
    #---------------------------------------------------------------------------------------------
    config['CalendarServiceEnabled'] = True
    config['GOOGLE_CALENDAR_TOKEN'] = secret_config.GOOGLE_CALENDAR_TOKEN

    #---------------------------------------------------------------------------------------------
    # Sun service
    #---------------------------------------------------------------------------------------------
    config['SunServiceEnabled'] = True

    #---------------------------------------------------------------------------------------------
    # Scale service
    #---------------------------------------------------------------------------------------------

    config['ScaleServiceEnabled'] = False
    config['CONSUMER_KEY']        = secret_config.NOKIA_CONSUMER_KEY
    config['CONSUMER_SECRET']     = secret_config.NOKIA_CONSUMER_SECRET
    config['OAUTH_VERIFIER']      = secret_config.NOKIA_OAUTH_VERIFIER
    config['ACCESS_TOKEN']        = secret_config.NOKIA_ACCESS_TOKEN
    config['ACCESS_TOKEN_SECRET'] = secret_config.NOKIA_ACCESS_TOKEN_SECRET
    config['NOKIA_USER_ID']       = secret_config.NOKIA_USER_ID
    

    #---------------------------------------------------------------------------------------------
    # TV service
    #---------------------------------------------------------------------------------------------
    config['TvServiceEnabled'] = False
    config['TvServiceTimeout'] = 300
    config['HARMONY_IP_ADRESS'] = '192.168.2.143'
    config['WATCH_TV_ACTIVITY'] = '47271415'
    
    #---------------------------------------------------------------------------------------------
    # Connectivity service
    # Check internet connectivity
    #---------------------------------------------------------------------------------------------
    config['ConnectivityServiceEnabled'] = False
    
    #---------------------------------------------------------------------------------------------
    # Fibaro service
    # Monitor Fibaro system alarm state.
    #---------------------------------------------------------------------------------------------
    config['FibaroServiceEnabled'] = True
    config['FibaroTimeout'] = 300
    config['FibaroVirtualDeviceId'] = "69"

    #---------------------------------------------------------------------------------------------
    # DishWashService
    # Determine when dishwascher is ready with a Fibaro power plug
    #---------------------------------------------------------------------------------------------
    config['DishWashServiceEnabled'] = True
    #---------------------------------------------------------------------------------------------
    # DepartureService
    # Fetch 
    #---------------------------------------------------------------------------------------------
    config['DepartureServiceEnabled'] = True
    config['DEPARTURE_SETTING'] = secret_config.SL_API_KEYS

   
    #---------------------------------------------------------------------------------------------
    # PowerUsageService
    # Measure usage time of certain devices with a Fibaro power plug. 
    #---------------------------------------------------------------------------------------------
    config["PowerUsageServiceEnabled"] = True

    #---------------------------------------------------------------------------------------------
    # PowerUsageService
    # Measure usage time of certain devices with a Fibaro power plug. 
    #---------------------------------------------------------------------------------------------
    config["TradfriServiceEnabled"] = True
    config['TRADFRI_GATEWAY_IP'] = "192.168.50.4"
    config['TRADFRI_ID'] = "tradfri-pi-bash" 
    config['TRADFRI_ID_KEY'] = secret_config.TRADFRI_KEYS

    config['TRADFRI_DEVICE_TYPES'] = [
        # DeviceTypeName       DeviceTypeId,             Close/Off/Min,   Open/On/Max
        'SocketController,         3311,       5850,         0,         1,',
        'BlindController,          15015,      5536,         0,        100',
        'GroupController,          3311,       5850,         0 ,        1',
        'DriverController,         3311,       5851,         5,        250'
    ]

    config['TRADFRI_DEVICES'] = [
              # Name        |    ID,      |      DeviceType
              'ljusslinga,      65563,         SocketController',
              'Julgran,         65591,         SocketController',
              'ViggoWindow,     65539,         SocketController',
              'ViggoShelf,      65540,         SocketController',
              'ViggoBlind,      65584,         BlindController',                 
              'WilmaWindow,     65541,         SocketController',
              'WilmaSlinga,     65542,         SocketController',
              'WilmaBlindRight, 65598,         BlindController',                 
              'WilmaBlindLeft,  65599,         BlindController',                 
              'Datarum,         65544,         SocketController',
              'Tavla,           65545,         SocketController',
              'Gillestuga,      65547,         SocketController',
              'Sovrum,          65546,         SocketController',
              'TvRoomLamp,      65577,         SocketController',
              'TvRoomWindow,    65578,         SocketController',
              'TvRoomGroup,    [TvRoomLamp TvRoomWindow],       GroupController',
              'Skrubben,        65579,         SocketController',
              'Sminklampa,      65580,         SocketController',
              'Vitrin,          65581,         SocketController',
              'VitrinDimmer,    65581,         DriverController',
              'KitchenGroup,    [ljusslinga Vitrin],       GroupController',
              'EcowittGateway,     65585,      SocketController',
              'TvRumTvToggle,      65604,      SocketController',
              'KitchenLjusstakar,  65605,      SocketController',
              'KitchenTvToggle,    65608,      SocketController',
              'GillestugaTvToggle, 65607,      SocketController',
    ]


    #---------------------------------------------------------------------------------------------
    # MoistureMonitorService
    # Measure usage time of certain devices with a Fibaro power plug. 
    #---------------------------------------------------------------------------------------------
    config['MoistureMonitorServiceEnabled'] = True
    config['MoistureMonitorTimeout'] = 900
    config['MoistureVdId']="298"
    config['MoistureMaxLimit']=75


    config['AdaxServiceEnabled'] = True

    #---------------------------------------------------------------------------------------------
    # Common services
    #---------------------------------------------------------------------------------------------
    config["AlarmServiceEnabled"] = True
    config["DatabaseServiceEnabled"] = True
    config["DataBaseTablePath"] = config["ROOT"] + '/db/davan.db'
    #/opt/grafana/davan.db

    #---------------------------------------------------------------------------------------------
    # ExternalEvent service
    #---------------------------------------------------------------------------------------------
    config["ExternalEventServiceEnabled"] = False

    #---------------------------------------------------------------------------------------------
    # Tuya service
    #---------------------------------------------------------------------------------------------
    config["TuyaServiceEnabled"] = True
    config["TuyaUsername"] = secret_config.TUYA_USER 
    config["TuyaPassword"] = secret_config.TUYA_PWD
    config["TuyaCountryCode"] = '46'
    config["TuyaBizType"] = 'smart_life'
    config["TuyaDevices"] = [
#      'Stair_Light':['Stair_Color','Stair_off'],
#      'Tv_Light':['Tv_Color','Tv_off'],
#      'Upstairs_Light':['Upstairs_Color','Upstairs_Off']
        'Stair_Light','Stair_Color', 'Stair_sc', 'Stair_sc_1', 'Stair_sc_2','Stair_sc_3', 'Stair_sc_4','Stair_off',
        'Tv_Light','Tv_Color', 'Tv_sc', 'Tv_sc_1', 'Tv_sc_2','Tv_sc_3', 'Tv_sc_4','Tv_off',
        'Upstairs_Light', 'Upstairs_Color','Upstairs_Off',
    ]


    #---------------------------------------------------------------------------------------------
    # Robomow service
    #---------------------------------------------------------------------------------------------
    config["RobomowServiceEnabled"] = True
    config['FIBARO_VD_ROBOMOW_ID'] = "340"
    # Mappings of users and the label in the presense virtual device
    config['FIBARO_VD_ROBOMOW_MAPPINGS'] = {
      # User    : HC2 Virtualdevice ID
        'State' : 'ui.Label1.value',
        'Changed' : 'ui.Label2.value'}

    config['FIBARO_VD_ROBOMOW_ID_1'] = "424"
    config['FIBARO_VD_ROBOMOW_MAPPINGS_1'] = {
      # User    : HC2 Virtualdevice ID
        'Date' : 'ui.date.value',
        'Status' : 'ui.status.value',
        'Activity':'ui.activity<id>.value'}

    #---------------------------------------------------------------------------------------------
    # Doorbell service
    #---------------------------------------------------------------------------------------------
    config["DoorbellServiceEnabled"] = True

    #---------------------------------------------------------------------------------------------
    # Volumio service
    #---------------------------------------------------------------------------------------------
    config["VolumioServiceEnabled"] = True
    config["VOLUMIO_HOST"] = '192.168.50.92'
    config["VOLUMIO_USER"] = secret_config.VOLUMIO_USER
    config["VOLUMIO_PWD"] = secret_config.VOLUMIO_PWD


    config["HarmonyServiceEnabled"]=True
    config["CameraServiceEnabled"] = False

    #---------------------------------------------------------------------------------------------
    # Roomba service
    #---------------------------------------------------------------------------------------------
    config["RoombaServiceEnabled"] = True
    config["ROOMBA_HOST"] = '192.168.2.155'
    config["ROOMBA_USER"] = secret_config.ROOMBA_USER
    config["ROOMBA_PWD"] = secret_config.ROOMBA_PWD
    config['FIBARO_VD_ROOMBA_ID'] = "433"
    config['FIBARO_VD_ROOMBA_MAPPINGS'] = {
      # User    : HC2 Virtualdevice ID
        'Battery' : 'ui.battery.value',
        'State'   : 'ui.state.value',
        'Bin'    : 'ui.bin.value',
        'Time'    : 'ui.time.value'}
    config['ROOMBA_ROOM_MAPPINGS'] = {
      # Roomname    : Roomba ID
        'wilma'       : '15',
        'viggo'       : '14',
        'kok'         : '9',
        'matsal'      : '1',
        'tvattstuga'  : '16',
        'hall'        : '12'}

    config["EcowittServiceEnabled"] = True
    config['FIBARO_VD_ECOWITT_ID'] = "435"
    config['FIBARO_VD_ECOWITT_POOL_ID'] = "439"
    config['FIBARO_VD_ECOWITT_POOL_MAPPINGS'] = {
      # User    : HC2 Virtualdevice ID
      #  'temp1c'    : ['ui.utespa.value',''],
        'tf_ch1c' : ['ui.utespa.value',''],
        'tf_ch2c' : ['ui.pool.value','']
        
}

    config['FIBARO_VD_ECOWITT_MAPPINGS'] = {
      # User    : HC2 Virtualdevice ID
        'tempc' : ['ui.temp.value'],
        'humidity' : ['ui.humidity.value',''],
      #  'soilmoisture1' : ['ui.soil1.value','Tomat',20],
      #  'soilmoisture2' : ['ui.soil2.value','Gurka',30],
      #  'temp1c' : ['ui.pool.value',''],
        #'pm25_ch1' : ['ui.air.value',''],
        'rainratemm'      : ['ui.now.value',''],
        'hourlyrainmm'     : ['ui.hour.value',''],
        'dailyrainmm'     : ['ui.day.value',''],
        'yearlyrainmm'    : ['ui.year.value',''],
        'totalrainmm'     : ['ui.total.value',''],
        'weeklyrainmm'    : ['ui.week.value','']}

    config["EcowittMonitorServiceEnabled"] = True
    config["EcowittMonitorSocketController"] ="EcowittGateway"

    config['WaterLevelMonitorServiceEnabled'] = True
    config['WaterLevelMinLimit'] = 55
    config['WaterLevelMaxLimit'] = 20

    config['IceBreakerServiceEnabled'] = False
    config['ICEBREAKER_ID'] = "441"

    config['PumpMonitorServiceEnabled'] = True
    config['FIBARO_VD_PUMP_ID'] = "449"
    config['FIBARO_VD_PUMP_MAP'] = {
        'volume' : 'ui.volume.value',
        'interval' : 'ui.interval.value',
        'date' : 'ui.date.value',
        'distance' : 'ui.distance.value'

     }
    config['LogDatabaseServiceEnabled'] = True
    config['ImouCameraServiceEnabled'] = True


def create(private_config_file="/home/pi/private_config.py", debugPrint=False):
    if (not private_config_file == None and len(private_config_file) > 0 and os.path.exists(private_config_file)):
        try:
            filename = os.path.basename(private_config_file)
            modulename = os.path.splitext(filename)[0]
            my_secrets = imp.load_source(modulename, private_config_file)
        except :
            print("Cannot import file " + private_config_file +" using default")
            from . import no_private_config
            my_secrets = no_private_config
    else:
        from . import no_private_config
        my_secrets = no_private_config
            
    config = dict()
    create_config(my_secrets, config)
    if debugPrint:
        common.debug_formated(config)
    return config


