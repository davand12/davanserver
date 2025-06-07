import logging.handlers
from logging.handlers import TimedRotatingFileHandler
import os
import time
import inspect


levels = [('CRITICAL' , logging.CRITICAL),
          ('ERROR' , logging.ERROR),
          ('WARNING' , logging.WARNING),
          ('INFO' , logging.INFO),
          ('DEBUG' , logging.DEBUG)]

def start_file_logging(log_file_path, loglevel=4,log_file_name =""):
    """
    Starts logging to file. Rotate file at midnight, keep 30 logfiles 
    """
    if not os.path.exists(log_file_path):
        os.makedirs(log_file_path)

    if not log_file_name:
        log_file_name = get_caller_name()

    logfile = log_file_path + '/' + log_file_name +'.log'
    masterLog = logging.getLogger('')
    masterLog.setLevel(levels[loglevel][1])
    masterHandler = TimedRotatingFileHandler(logfile, 'MIDNIGHT', backupCount=30)
    formatter = logging.Formatter('%(asctime)s %(name)-35s %(levelname)-8s %(message)s',"%H:%M:%S")
    masterHandler.setFormatter(formatter)
    logging.getLogger('').addHandler(masterHandler)

def stop_file_logging(file_name):
    """
    Stop logging to the file file_name, by 
    removing the filehandler.  
    """
    for handler in logging.root.handlers[:]:
        if isinstance(handler, logging.FileHandler ):
            if os.path.basename(handler.baseFilename) == file_name:
                logging.root.removeHandler(handler)
                return

def stop_logging():
    """
    Stop logging
    """
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


def start_logging(log_file_path, loglevel=4, log_file_name=""):
    """
    Start logging to file and console
    @param log_file_path path to store logfile
    @param loglevel loglevel of console logging
    @param log_file_name logfile name
    """
    if loglevel < 0 or loglevel > 5 :
        loglevel = 4
    if not os.path.exists(log_file_path):
        os.makedirs(log_file_path)
    if not log_file_name:
        log_file_name = get_caller_name()

    logfile = log_file_path + '/' + log_file_name + '_' + time.strftime("%Y-%m-%d_%H%M%S", time.localtime()) + '.log'
    logging.basicConfig(level=levels[loglevel][1],
                    format='%(asctime)s %(name)-35s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=logfile,
                    filemode='w')
    console = logging.StreamHandler()
    console.setLevel(levels[loglevel][1])

    formatter = logging.Formatter('%(name)-35s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    logger = logging.getLogger(os.path.basename(__file__))
    logger.info('Log setting: Console['+ levels[loglevel][0] +'] File[DEBUG] Logfile[' + logfile + ']')    
    
def get_caller_name():
    """
    Returns the filename of the calling module.
    """
    _, filename, _, _, _, _ =\
        inspect.getouterframes(inspect.currentframe())[2]
    log_file_name = os.path.splitext(os.path.basename(filename))[0]
    return log_file_name

def get_logfile_name():
    """
    Return the current logfile name
    """
    return logging.getLoggerClass().root.handlers[0].baseFilename

def change_loglevel(loglevel):
    """
    """
    logging.getLogger().setLevel(levels[loglevel][1])
    logger = logging.getLogger(os.path.basename(__file__))
    logger.log(levels[loglevel][1],"Changing loglevel to " + levels[loglevel][0] )

# def change_loglevel(loglevel):
#     """
#     Change the loglevel in console.
#     Stop all console logging and then start it again with the new loglevel.
#     Logging to file and via tcp is kept.
#     """
#     for handler in logging.root.handlers[:]:
#         if isinstance(handler, logging.FileHandler ): # dont change filelogging
#             continue
#         elif isinstance(handler, logging.handlers.SocketHandler): # dont change streamlogging
#             continue
#         else: #
#             logging.root.removeHandler(handler)
# 
#     console = logging.StreamHandler()
#     console.setLevel(levels[loglevel][1])
#     formatter = logging.Formatter('%(name)-35s: %(levelname)-8s %(message)s')
#     # tell the handler to use this format
#     console.setFormatter(formatter)
#     # add the handler to the root logger
#     logging.getLogger('').addHandler(console)
#     logger = logging.getLogger(os.path.basename(__file__))
#     logger.log( levels[loglevel][1],"Changing console loglevel to " + levels[loglevel][0] )

