import logging
import os
import davan.util.helper_functions as helper 
from davan.util.StateMachine import StateMachine
from  davan.util.StateMachine import State

STARTED = 1
CANCELLED = 0
INITIAL = 0
LIMIT = 5


class BaseState(State):
    def __init__(self, temp, configured_temp):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.temp = temp
        self.configured_temp = configured_temp
        self.transition = 0

class InitialState(BaseState):
    def __init__(self, temp=-1, configured_temp=-1):
        BaseState.__init__( self,temp, configured_temp )
    
    def handle_data(self, current_temp):
        self.temp = current_temp
        self.configured_temp = current_temp

    def next(self):
        return NoHeatingState(self.temp,self.configured_temp)

    def get_message(self):
        return "Uppdaterar pool inställningarna, önskad temp ["+str(self.configured_temp)+"] nuvarande temp ["+str(self.temp)+"]"


class HeatingMaxReachedState(BaseState):
    def __init__(self, temp, configured_temp):
        BaseState.__init__( self, temp, configured_temp )
    
    def handle_data(self, current_temp):
        if current_temp < self.temp:
            self.transition += STARTED
        
        elif current_temp > self.temp:
            self.logger.debug("Still heating, current temp["+str(current_temp)+"] < configured temp["+str(self.configured_temp)+"]")                
            self.transition = CANCELLED

        if current_temp >= self.configured_temp:
            self.configured_temp = current_temp

        self.temp = current_temp


    def next(self):
        if self.transition == LIMIT:
            return NoHeatingState(self.temp, self.configured_temp)

    def get_message(self):
        return "Poolen har uppnått önskad temperatur ["+str(self.configured_temp)+"]"


class HeatingState(BaseState):
    def __init__(self, temp, configured_temp):
        BaseState.__init__( self, temp, configured_temp )
            
    def handle_data(self, current_temp):
        if current_temp >= self.configured_temp:
            self.configured_temp = current_temp
            self.transition += STARTED
        
        elif current_temp < self.temp:
            self.logger.warning("Temp is decreasing without reaching the configured temp, current temp["+str(current_temp)+"] < configured temp["+str(self.configured_temp)+"]")                            
            self.transition += STARTED

        else:
            self.logger.debug("Continue heating, current temp["+str(current_temp)+"] < configured temp["+str(self.configured_temp)+"]")                
            self.transition = CANCELLED
        
        self.temp = current_temp

    def next(self):
        if self.transition >= LIMIT:
            if self.temp >= self.configured_temp:
                return HeatingMaxReachedState(self.temp, self.configured_temp)
            return InitialState(self.temp, self.configured_temp)

    def get_message(self):
        return "Startar värmaren i poolen"

class NoHeatingState(BaseState):
    def __init__(self, temp, configured_temp):
        BaseState.__init__( self, temp, configured_temp )
    
    def handle_data(self, current_temp):
        if current_temp > self.temp :
            self.transition += STARTED
        
        elif current_temp < self.temp:
            self.transition = CANCELLED

        self.temp = current_temp

    def next(self):
        if self.transition >= LIMIT:
            return HeatingState(self.temp, self.configured_temp)
        else:
            self.logger.debug("Heating not started")

    def get_message(self):
        return "Stänger av värmaren"

class PoolTempHandle():
    '''
    Constructor
    '''
    def __init__(self, config,id, name):
        self.logger = logging.getLogger(os.path.basename(__file__))

        self.config = config
        self.sm = StateMachine(config, InitialState())
        self.id = id
        self.name = name
        self.logger.info("Initialize PoolTempHandle " + self.name)

    def handle_data(self, data):
        '''
        Process the recevied pool temp data
        '''
        if not self.id in data:
            return
            
        current_temp = data[self.id]

        #self._log_state(current_temp)

        # Check limit
        #if current_temp < 5 :    
        #    self.logger.warning("Temperaturen i pool är " + str(current_temp) + " grader, vilket är för lågt!")
        #    helper.send_telegram_message(self.config, "Temperaturen i pool är " + str( current_temp) + " grader, vilket är för lågt!") 

        self.sm.handle_data(current_temp)
        next_state = self.sm.next() 
        
        if next_state:
            self.sm.change_state(next_state)

    def _log_state(self,new_temp):
        '''
        Log the current state and temp
        '''
        state = self.sm.currentState
        self.logger.debug("State["+state.__class__.__name__+ "] Temp ["+str(state.temp)+"] -> ["+str(new_temp)+"]")        
