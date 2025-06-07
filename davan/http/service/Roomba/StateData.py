import os
import logging

class StateData():
    def __init__(self, config, services):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.config = config
        self.services = services
        self.bin_full = False
        self.batPct = ""
        self.roomname = ""
        self.error_status =""
        self.region = ""
        self.current_phase =""
