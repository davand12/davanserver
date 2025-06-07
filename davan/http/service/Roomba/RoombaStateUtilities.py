'''
@author: davandev 
sys.setdefaultencoding('latin-1')
'''
import os
import logging
import davan.util.helper_functions as helper 
import davan.http.service.roomba.RoombaStateUtilities as StateUtil
import davan.util.constants as constants


global logger
logger = logging.getLogger(os.path.basename(__file__))

states = {"Charging"          : "Laddar",
            "new"             : "Nytt uppdrag",
            "New Mission"     : "Nytt uppdrag",            
            "Running"         : "Städar",
            "resume"          : "Fortsätter städa",
            "hmMidMsn"        : "Dockning",
            "recharge"        : "Laddar",
            "Stuck"           : "Fastnat",
            "hmUsrDock"       : "Användar dockning",
            "Mission Completed"       : "Städning färdig",
            "cancelled"       : "Avbruten",
            "Stopped"            : "Stoppad",
            "pause"           : "Pausad",
            "evac"            : "Tömmer",
            "hmPostMsn"       : "På väg hem",
            "chargingerror"   : "Fel på laddning",
            "Standby"         : "Vilar",
            "Docking - End Mission": "Dockning",

            ""                :  None}


# from various sources
_ErrorMessages = {
    1:["Ojämn yta. Placera på en plan yta och tryck sedan på Clean-knappen","Roombas vänstra hjul hänger ner eller så sitter Roomba fast."],
    2:["Rengör borstarna och tryck sedan på Clean-knappen","Flerytborstarna av gummi kan inte snurra."],
    3:["Ojämn yta. Placera på en plan yta och tryck sedan på Clean-knapp","Roombas högra hjul hänger ner eller så sitter Roomba fast."],
    4:["Rengör hjulen och tryck sedan på Clean-knappen","Vänster hjul sitter fast. Vänster hjul sitter fast"],
    5:["Rengör hjulen och tryck sedan på Clean-knappen","Höger hjul sitter fast. Höger hjul sitter fast"],
    6:["Avlämning detekterad. Flytta till ett nytt område och tryck sedan på Clean-knappen","Konstant kant detekterad. Kontrollera att kantsensorerna är fria från skräp"],
    7:["Hjulproblem. Mer information finns i appen","Vänster hjul på marken och robot känner inte av"],
    8:["Dammsugarproblem. Mer information finns i appen","Dammsugaren har dålig sugkraft"],
    9:["Knacka på stötfångaren för att lösgöra"," tryck sedan på Clean-knappen","Konstant skumpande. Stötfångaren har samlat på sig skräp eller har lossnat"],
    10:["Hjulproblem. Mer information finns i appen","Höger hjul på marken och robot känner inte av"],
    11:["Dammsugarproblem. Mer information finns i appen","Dammsugarmotorn aktiveras inte"],
    12:["Avlämning detekterad. Flytta till ett nytt område och tryck sedan på Clean-knappen","Kantsensorer"],
    13:["Ojämn yta. Placera på en plan yta och tryck sedan på Clean-knappen","Båda hjulen på ojämn yta"],
    14:["Återmontera behållaren och tryck sedan på Clean-knappen","Behållaren sitter inte på roboten. Se till att ett filter är monterat i behållaren. Kontrollera brytaren för behållardetektering"],
    15:["Internt kretskortfel","Internt kretskortfel"],
    16:["Flytta till en plan yta och tryck sedan på Clean-knappen","Robot skumpar till vid start. Stötfångaren kan ha lossnat"],
    17:["Navigeringsproblem. Mer information finns i appen","Roboten kom in i ett okänt område och åkte vilse under rengöringen och kunde inte återvända till basstationen"],
    18:["Dockningsproblem. Placera på basstationen för att ladda","Rengöringen är färdig, men roboten kunde inte docka till basstationen"],
    19:["Avdockningsproblem. Ta bort hinder och tryck sedan på CLEAN","Det gick inte att avdocka. Kan ha stött till något i närheten av basstationen"],
    20:["Mer information finns i appen","Roomba  har ett internt kommunikationsfel."],
    21:["Mer information finns i appen","Förlorat kommunikation med mobilitetskretsen. Starta om roboten. Om problemet kvarstår, byt ut"],
    22:["Flytta till ett nytt område och tryck sedan på CLEAN","Roombas omgivning"],
    23:["","Fel vid batteriautentisering. Kontrollera att batteriet är ett iRobot-batteri i originalutförande"],
    24:["Placera på en plan yta och tryck sedan på Clean-knappen","Roombas omgivning"],
    25:["Mer information finns i appen","Internt kretskortfel. Starta om roboten. Om problemet kvarstår, byt ut"],
    26:["Dammsugarproblem. Mer information finns i appen","Dammsugarstopp. Filterpropp möjlig"],
    27:["Dammsugarproblem. Mer information finns i appen","Dammsugarmotor överhettad: Tilltäppt filter eller dåligt pumphjul i dammsugarmotorn"],
    29:["Mer information finns i appen","Fel vid uppgradering av programvara"],
    30:["Dammsugarproblem. Mer information finns i appen","Dammsugaren startade inte"],
    31:["Mer information finns i appen","Internt kretskortfel. Tryck på CLEAN-knappen för att starta om."],
    32:["Mer information finns i appen","Smart Map-versionen i roboten matchar inte den karta som finns sparad i appen"],
    33:["Flytta till ett nytt område och tryck sedan på CLEAN-knappen","Roboten kan inte städa den väg som stakats ut i Smart Map. Vägen kan vara blockerad"],
    34:["Mer information finns i appen","Internt kommunikationsfel. Starta om roboten. Om problemet kvarstår, byt ut"],
    36:["Töm behållaren","Sensorn för full behållare ej nollställd efter utrensning av skräp"],
    38:["Mer information finns i appen","Strömkommunikation Problem. Starta om roboten. Om problemet kvarstår, byt ut"],
    39:["Mer information finns i appen","Strömkommunikation Problem. Starta om roboten. Om problemet kvarstår, byt ut"],
    40:["","Robot fastnat i Virtual Wall-stråle"],
    41:["Mer information finns i appen","Uppdraget avbröts innan slutförande. Tryck på CLEAN-knappen för att starta om uppdraget"],
    42:["","Kunde inte omlokalisera vid direkt städning"],
    43:["","Startade i basstationens IR-fält från basstationen"],
    46:["Låg batterinivå. Ladda","Roboten avslutade uppdraget med låg batterinivå utan att docka"],
    47:["Mer information finns i appen","Ogiltig robotkalibrering. Starta om roboten. "],
    48:["Roombas väg","Ogiltig robotkalibrering. Starta om roboten."]
}

def extract_data(message, stateData):
    if message.topic == "/roomba/feedback/Bogda/state" :
        new_phase = message.payload.decode()
        if new_phase != stateData.current_phase:
            logger.info(f"Topic[`{message.topic}`] Payload[`{message.payload.decode()}`]")
            stateData.current_phase = new_phase

    if message.topic == "/roomba/feedback/cleanMissionStatus_error" :
        logger.info(f"Topic[`{message.topic}`] Payload[`{message.payload.decode()}`]")
        stateData.error_status = message.payload.decode()
    
    if message.topic == "/roomba/feedback/Bogda/error_message" :
        payload = message.payload.decode()
        if payload != 'None':
            logger.info(f"Topic[`{message.topic}`] Payload[`{payload}`]")

    if message.topic == "/roomba/feedback/Bogda/lastCommand_regions" :
        new_region = message.payload.decode()
        if new_region != stateData.region:
            logger.info(f"Topic[`{message.topic}`] Payload[`{message.payload.decode()}`]")
            stateData.region = new_region
            stateData.roomname = str(get_roomname_from_region(stateData))
            if stateData.current_phase == 'Running':
                helper.send_telegram_message( stateData.config,"Dammsuger [" + stateData.roomname + "]")

    if message.topic == "/roomba/feedback/Bogda/batPct" :
        new_batpct = message.payload.decode()
        if new_batpct != stateData.batPct:
           logger.info(f"Topic[`{message.topic}`] Payload[`{message.payload.decode()}`]")
           stateData.batPct = new_batpct
    
    if message.topic == "/roomba/feedback/Bogda/bin_full" :
        new_value = message.payload.decode()
        if new_value != stateData.bin_full:
            logger.info(f"Topic[`{message.topic}`] Payload[`{message.payload.decode()}`]")
            stateData.bin_full = new_value
            


def notify( stateData ):        
    if stateData.current_phase == 'Stuck':
        error_number = stateData.error_status
        if error_number != "":
            error_swe = StateUtil._ErrorMessages[error_number]
            logger.warning("Error msg: "+ str(error_swe[0]))
            helper.send_telegram_message(stateData.config, "Bogda[ "+error_swe[1]+" ]")
            error_swe="Bogda har fastnat och behöver hjälp, " + error_swe[1]+" "+ error_swe[0]
            stateData.services.get_service(constants.TTS_SERVICE_NAME).start(
                    error_swe,
                    constants.SPEAKER_KITCHEN)

    if stateData.bin_full == True:
        helper.send_telegram_message(stateData.config, "Bogda[ Töm damm behållaren ]")
        stateData.services.get_service(
            constants.TTS_SERVICE_NAME).start(
                constants.ROOMBA_EMPTY_BIN,
                constants.SPEAKER_KITCHEN)

def get_ids( stateData ):
    ids = []
    try:
       regions = stateData.region.split('),')
       for region in regions:
          logger.debug("Region: "+str(region))
          if 'region_id' in region:
              region = region.replace("(","")
              region = region.replace(")","")
              region = region.replace("'","")
              ids.append( (region.split(',')[1]).strip() )
    except Exception as e:
       logger.info(str(e))
    return ids

def get_roomname_from_region( stateData ):
    ids = get_ids(stateData)
    roomnames = []
    s =""
    rooms = stateData.config['ROOMBA_ROOM_MAPPINGS']
    for id in ids:
        for name, room_id in rooms.items():
            logger.debug('Name:' + name + " Id:" + room_id)
            if id == room_id:
                logger.info("Dammsuger[" + name + "]")
                roomnames.append( name + " ")
    return s.join(roomnames) 
