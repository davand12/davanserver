import logging
import os
import davan.util.helper_functions as helper 
from davan.util.StateMachine import StateMachine
from  davan.util.StateMachine import State

class RainingState(State):
    def __init__(self):
        State.__init__( self )
        self.transition = 0
    
    def handle_data(self,rainrate):
        if rainrate > 0 :
            self.transition = 0
        else:
            self.transition += 1
            self.logger.debug("Verkar slutat regna "+ str(self.transition))

    def next(self):
        if self.transition == 5:
            return NoRainState()
        return None

    def get_message(self):
        return "Det har börjat regna"


class NoRainState(State): 
    def __init__(self):
        State.__init__( self )
        self.transition = 0
    
    def handle_data(self, rainrate):
        if rainrate > 0 :
            self.transition += 1
            self.logger.debug("Verkar börjat regna "+ str(self.transition))
        else:
            self.transition = 0

    def next(self):
        if self.transition == 5:
            return RainingState()
        return None

    def get_message(self):
        return "Det har slutat regna"


class RainHandle():

    '''
    Constructor
    '''
    def __init__(self, config):
        self.logger = logging.getLogger(os.path.basename(__file__))
        
        self.sm = StateMachine(config, RainingState())
        self.logger.info("Initialize RainHandle")

    def handle_data(self, data):
        '''
        Process the recevied rain rate data
        '''
        rainrate = data['rainratemm']
        self.sm.handle_data(rainrate)
        next_state = self.sm.next() 
        
        if next_state:
            self.sm.change_state(next_state)