import logging
import os
import davan.util.helper_functions as helper 
from davan.util.StateMachine import StateMachine
from davan.util.StateMachine import State


class MoistureStateBase(State):
    def __init__(self, id, name, level, limit):
        State.__init__( self )
        self.limit = limit 
        self.device_name = name
        self.id = id
        self.level =level

    def handle_data(self, current_level):
        self.logger.debug(self.device_name+": State["+self.__class__.__name__+"] Current["+str(current_level)+"] Limit["+ str(self.limit)+"] ")
        self.level = current_level

class WetState(MoistureStateBase):
    def __init__(self, id, name, level, limit):
        MoistureStateBase.__init__(self, id, name, level, limit)

    def next(self):
        if self.level < self.limit :
            return DryState(self.id, self.device_name, self.level, self.limit)

    def get_message(self):
        return "Fuktnivån "+self.device_name+" ["+str(self.level)+"% ] är ok"

class DryState(MoistureStateBase):
    def __init__(self, id, name, level, limit):
        MoistureStateBase.__init__(self, id, name, level, limit)

    def next(self):
        if self.level > self.limit :
            return WetState(self.id, self.device_name, self.level, self.limit)

    def get_message(self):
        return self.device_name+"[ "+str(self.level)+"% ] behöver vattnas"

class MoistureHandle():
    '''
    Constructor
    '''
    def __init__(self, config):
        self.logger = logging.getLogger(os.path.basename(__file__))

        self.config = config
        self.sm = []

        for id in self.config['FIBARO_VD_ECOWITT_MAPPINGS'].keys():
            if 'soilmoisture' in id:

                name = self.config['FIBARO_VD_ECOWITT_MAPPINGS'][id][1]
                limit = self.config['FIBARO_VD_ECOWITT_MAPPINGS'][id][2]
                state = WetState(id, name, -1, limit)
                self.sm.append(StateMachine(config, state))
                self.logger.info("Adding monitoring of moisture device "+name+"["+str(limit)+"]")

    def handle_data(self, data):
        '''
        Process the recevied rain rate data
        Iterate all configured sensors and compare with limits 
        '''

        for monitor in self.sm:
            id = monitor.currentState.id
            if id in data.keys():
                
                current_level = data[id]
                monitor.handle_data(current_level)
                next = monitor.next()
                if next:
                    monitor.change_state(next) 