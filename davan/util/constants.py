'''
@author: davandev 
sys.setdefaultencoding('latin-1')
'''

RESPONSE_OK = 200
RESPONSE_NOT_OK = 401
RESPONSE_FILE_NOT_FOUND = "File not found"
RESPONSE_EMPTY_MSG = ""
RESPONSE_FAILED_TO_TAKE_PICTURE = "Failed to take picture"
RESPONSE_FAILED_TO_PARSE_REQUEST = "Failed to parse request"
TURN_ON = "turnOn"
TURN_OFF ="turnOff"

FAILED_TO_GENERATE_TTS = "Misslyckades att generera text-till-tal."
HUMIDITY_HIGH = "Fuktigt i badrummet, var god ventilera!"
CONFIGURATION_FAULT = "Fel i konfigurationen Keypad[%]"
KEYPAD_NOT_ANSWERING = "Alarm Keypad[%] har slutat svara"
KEYPAD_ANSWERING = "Alarm Keypad[%] har startats"
RAIN_STARTED = "Det har startat att regna"
RAIN_STOPPED = "Det har slutat att regna"
TELLDUS_NOT_ANSWERING = "Telldus svarar inte"
TRADFRI_NOT_ANSWERING = "Tradfri svarar inte"
TUYA_NOT_ANSWERING = "Tuya svarar inte"
ROBOMOW_FAILURE = "Fel vid hantering av request "
ROOMBA_EMPTY_BIN = "Bogdas dammbehållare är full, var snäll och tömm den"
UPS_SERVICE_NAME = "Ups"
TRADFRI_SERVICE_NAME = "TradfriService"
ECOWITT_SERVICE_NAME = "EcowittService"
ECOWITT_MONITOR_SERVICE_NAME = "EcowittMonitorService"
AUTH_SERVICE_NAME = "authenticate"
AUDIO_SERVICE_NAME = "AudioService"
SPEEDTEST_SERVICE_NAME = "SpeedtestService"
TTS_SERVICE_NAME =  "tts"
TTS_FETCHER_SERVICE_NAME =  "ttsCompleted"
QUOTE_SERVICE_NAME = "DailyQuote"
HTML_SERVICE_NAME = "HtmlService"
ACTIVE_SCENES_SERVICE_NAME = "ActiveScenesMonitor"
TELLDUS_SENSOR_SERVICE = "TelldusSensorService"
TELLDUS_SERVICE_NAME = "telldus"
PRESENCE_SERVICE_NAME = "presence"
DEVICE_PRESENCE_SERVICE_NAME = "DevicePresenceService"
MP3_SERVICE_NAME = "mp3"
SONOS_SERVICE_NAME = "SonosService"
WEATHER_SERVICE = "Weather"
LIGHTSCHEMA_SERVICE = "LightSchemaService"
KEYPAD_SERVICE_NAME = "KeypadAliveService"
RECEIVER_BOT_SERVICE_NAME = "ReceiverBotService"
ROXCORE_SPEAKER_SERVICE_NAME = "RoxcoreService"
VOLUMIO_SERVICE_NAME = "VolumioService"
ANNOUNCEMENT_SERVICE_NAME = "AnnouncementsService"
CALENDAR_SERVICE_NAME = "CalendarService"
SUN_SERVICE_NAME = "SunService"
TV_SERVICE_NAME = "TvService"
SCALE_SERVICE_NAME = "ScaleService"
CONNECTIVITY_SERVICE_NAME = "ConnectivityService"
FIBARO_SERVICE_NAME = "FibaroService"
DISHWASH_SERVICE_NAME = "DishWashService"
DEPARTURE_SERVICE_NAME = "DepartureService"
ALARM_SERVICE_NAME = "AlarmService"
POWER_USAGE_SERVICE_NAME = "PowerUsageService"
DATABASE_SERVICE_NAME = "DatabaseService"
TUYA_SERVICE_NAME ="TuyaService"
ROBOMOW_SERVICE_NAME ="RobomowService"
DOORBELL_SERVICE_NAME ="DoorbellService"
PICTURE_SERVICE_NAME="TakePicture"
CAMERA_SERVICE_NAME="CameraService"
ROOMBA_SERVICE_NAME="RoombaService"
DATABASE_LOGS_SERVICE_NAME="LogDatabaseService"
EXTERNAL_EVENT_SERVICE_NAME = "ExternalEventService"

MOISTURE_MONITOR_SERVICE_NAME = "MoistureMonitorService"
WATER_LEVEL_MONITOR_SERVICE_NAME = "WaterLevelMonitorService"
PUMP_MONITOR_SERVICE_NAME = "PumpMonitorService"
ICE_BREAKER_SERVICE_NAME = "IceBreakerService"
IMOU_CAMERA_SERVICE_NAME ="ImouCameraService"
HARMONY_SERVICE_NAME ="HarmonyService"

UPS_BATTERY_MODE = "BatteryMode"
UPS_POWER_MODE = "PowerMode"
UPS_STATUS_REQ = "Status"

HTML_EXTENSION = ".html"
CSS_EXTENSION = ".css"
MP3_EXTENSION = ".mp3"
MP3_EXTENSION1 = "-mp3"
OGG_EXTENSION = ".ogg"
OGG_EXTENSION1 = "-ogg"
WAV_EXTENSION = ".wav"
WAV_EXTENSION1 = "-wav"

MIME_TYPE_HTML = 'text/html'
MIME_TYPE_CSS = 'text/css'
MIME_TYPE_WAV = 'audio/wav'
MIME_TYPE_MP3 = 'audio/mpeg'
MIME_TYPE_OGG = 'audio/ogg'

SPEAKER_HALLWAY = "1"
SPEAKER_KITCHEN = "0"
SPEAKER_ALL = "2"


USER_AGENT_HEADERS= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
'Accept-Encoding': 'none',
'Accept-Language': 'en-US,en;q=0.8',
'Connection': 'keep-alive'}

HTML_TABLE_END = "</table>"
HTML_TABLE_START = """<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}

tr:nth-child(even) {
    background-color: #dddddd;
}
</style><table> <tr>
    <th>Service</th>
    <th>Successful</th> 
    <th>Error</th>
  </tr>"""

COLUMN_TAG="""
    <div id="column<COLUMN_ID>">
    <h3><SERVICE_NAME></h3>
    <ul>
    <SERVICE_VALUE>
    </ul>
    </div>
"""
