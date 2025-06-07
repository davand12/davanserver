import logging
import os
from davan.util.StateMachine import StateMachine
import davan.util.helper_functions as helper 
import davan.http.service.roomba.RoombaStateUtilities as StateUtil
from davan.http.service.roomba.StateData import StateData

import davan.util.constants as constants

class RoombaBaseState:
    def __init__(self, stateData ):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.stateData = stateData

    def handle_data(self, rainrate):
        assert 0, "run not implemented"
    def next(self):
        assert 0, "next not implemented"
    def get_message(self):
        assert 0, "next not implemented"
    def enter(self):
        pass
    def exit(self):
        pass
    
class Initial(RoombaBaseState):
    def __init__(self, stateData):
        RoombaBaseState.__init__( self, stateData )

    def handle_data(self, message ):
        StateUtil.extract_data( message, self.stateData)
        StateUtil.notify( self.stateData )

    def next(self):
        if self.stateData.current_phase == 'Charging':
            return Charging( self.stateData )
        elif self.stateData.current_phase == 'Running':
            return Cleaning( self.stateData )

    def get_message(self):
        pass

class ManualRun(RoombaBaseState):
    def __init__(self, stateData):
        RoombaBaseState.__init__( self, stateData )

    def handle_data(self, data ):
        pass

    def next(self):
        return Cleaning( self.stateData )

    def get_message(self):
        return "Startar städning --> " + self.stateData.roomname
    
class Charging(RoombaBaseState):
    def __init__(self, stateData):
        RoombaBaseState.__init__( self, stateData )
        self.stateData.roomname = ""
    
    def handle_data(self, message ):
        StateUtil.extract_data(message, self.stateData)
        StateUtil.notify( self.stateData )

    def next(self):
        if self.stateData.batPct == '100':
            return Standby( self.stateData )
        elif self.stateData.current_phase == 'Running':
            return Cleaning( self.stateData )
 
    def get_message(self):
        return "Bogda Laddar [" + self.stateData.batPct + "]"

class Standby(RoombaBaseState):
    def __init__(self, stateData):
        RoombaBaseState.__init__( self, stateData )
        self.stateData.roomname = ""
    
    def handle_data(self, message):
        StateUtil.extract_data(message, self.stateData)
        StateUtil.notify( self.stateData )

    def next(self):
        if self.stateData.current_phase == 'Running' or self.stateData.current_phase == 'New Mission':
            return Cleaning( self.stateData )

    def get_message(self):
        return "Bodga Standby"

class Cleaning(RoombaBaseState):
    def __init__(self, stateData):
        RoombaBaseState.__init__( self, stateData )

    def handle_data(self, message):
        StateUtil.extract_data(message, self.stateData)
        StateUtil.notify( self.stateData )

    def next(self):

        if self.stateData.current_phase == 'Docking - End Mission':
            return HeadingHome( self.stateData )
        elif self.stateData.current_phase == 'Mission Completed':
            return Charging( self.stateData )
        elif self.stateData.current_phase == 'Stuck':
            return Error( self.stateData )

    def get_message(self):
        if self.stateData.roomname:
            return "Bogda dammsuger ["+ self.stateData.roomname + "]"
        else:
            return "Bogda städar"

class HeadingHome(RoombaBaseState):
    def __init__(self, stateData):
        RoombaBaseState.__init__( self, stateData )

    def handle_data(self,message):
        StateUtil.extract_data(message, self.stateData )
        StateUtil.notify( self.stateData )

    def next(self):
        if self.stateData.current_phase == 'Mission Completed':
            return Charging( self.stateData )
        elif self.stateData.current_phase == 'Stuck':
            return Error( self.stateData )
        elif self.stateData.current_phase == 'Cancelled':
            return Error( self.stateData )
        elif self.stateData.current_phase == 'Stopped':
            return Error( self.stateData )

    def get_message(self):
        return "Bogda på väg hem"
    
class Error(RoombaBaseState):
    def __init__(self, stateData):
        RoombaBaseState.__init__( self, stateData )
    
    def handle_data(self, message):
        StateUtil.extract_data(message, self.stateData )
        StateUtil.notify( self.stateData )
 
    def next(self):
        if self.stateData.current_phase == 'Charging':
            return Charging ( self.stateData ) 
        elif self.stateData.current_phase == 'Running':
            return Cleaning ( self.stateData ) 

    def get_message(self):
        return "Bogda har problem"

class RoombaHandle():
    def __init__(self, config, services):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.data = StateData(config, services)
        self.sm = StateMachine(config, Initial( self.data ))
        self.logger.info("Initialize RoombaHandle")

    def handle_data(self, message):
        '''
        Process the recevied rain rate data
        '''
        self.sm.handle_data(message)
        next_state = self.sm.next() 
        
        if next_state:
            self.sm.change_state(next_state)