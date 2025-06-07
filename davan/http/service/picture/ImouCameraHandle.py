import logging
import os
import requests

import davan.util.helper_functions as helper 
from davan.util.StateMachine import StateMachine
from davan.util.StateMachine import State

class StateData():
    def __init__(self, camera_name, logger, config, services, data):
        self.services = services
        self.camera_name = camera_name
        self.logger = logger
        self.config = config
        self.data = None
     
class BaseState(State):
    def __init__(self, state_data):
        State.__init__( self)
        self.state_data = state_data


class ActiveState(BaseState):
    def __init__(self, state_data):
        BaseState.__init__(self, state_data)
    
    def handle_data(self, data):
        self.logger.info("handle_data ["+self.state_data.camera_name+"]["+self.__class__.__name__+"] ")
        self.state_data.data = data

    def next(self):
        if self.state_data.data['msgType'] == 'closeCamera':
            return InactiveState(self.state_data)
        if self.state_data.data['msgType'] == 'human':
            helper.send_telegram_message( self.state_data.config,"Rörelse upptäckt i kamera [" + self.state_data.camera_name + "]")

    def get_message(self):
        return "Aktiverar kamera["+self.state_data.camera_name+"]"

    def fetch_picture(self):
        url = self.state_data.data['picUrl'][0]
        self.logger.info("Url:" + str(url))
        
        data = requests.get(url).content
        f = open('img.jpg','wb')
        
        f.write(data)
        f.close()        

class InactiveState(BaseState):
    def __init__(self, state_data):
        BaseState.__init__(self, state_data)

    def handle_data(self, data):
        self.logger.info("handle_data ["+self.state_data.camera_name+"]["+self.__class__.__name__+"] ")
        self.state_data.data = data

    def next(self):
        if self.state_data.data['msgType'] == 'openCamera':
            return ActiveState(self.state_data)
        if self.state_data.data['msgType'] == 'human':
            helper.send_telegram_message( self.state_data.config,"Rörelse upptäckt i kamera [" + self.state_data.camera_name + "]")

    def get_message(self):
        return "Inaktiverar kamera["+self.state_data.camera_name+"]"


class ImouCameraHandle():
    '''
    Constructor
    '''
    def __init__(self, config, services, camera_name):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.logger.info("Initialize ImouCameraHandle[" + camera_name+ "]")
        
        state_data = StateData(camera_name, self.logger, config, services, None)
        self.sm = StateMachine(config, InactiveState(state_data))

    def handle_data(self, data):
        '''
        '''
        self.sm.handle_data( data )
        next = self.sm.next()
        if next:
            self.sm.change_state(next)