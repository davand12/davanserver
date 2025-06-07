import logging
import subprocess
import sys
import os

global logger
logger = logging.getLogger(os.path.basename(__file__))

def execute_block_in_shell(command, process_debug_name=""):
    p = subprocess.Popen(command,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    _, _= p.communicate()

    if p.returncode == 1:
        return False
    else:
        return True

def execute_block(command, process_debug_name="",return_output=False):
    p = subprocess.Popen(command,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         encoding="utf-8" )
    out, err = p.communicate()

    if return_output:
        return str(out)

    logger.debug(str(out) + "Error:" + str(err))
    
    if p.returncode == 1:
        return False
    else:
        return True


def execute(command, process_debug_name=""):
    child = subprocess.Popen(command+" 1>&2", shell=True,
                     bufsize=0,
                     stderr=subprocess.PIPE,
                     stdout=subprocess.PIPE,)
    _read_process_output(child, process_debug_name)
    if child.returncode == 1:
        return False
    else:
        return True

def _read_process_output(process, process_debug_name):
        out = ""
        while True:
            out += process.stderr.readline().decode()
            sys.stderr.flush()
            if out == '' and process.poll() != None:
                break

            if out.endswith("\n"):
                logger.debug("[" + process_debug_name + "] : " + out.rstrip())
                out = ""
