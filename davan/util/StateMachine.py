import logging
import os
import davan.util.helper_functions as helper 
import inspect


STARTED = 1
CANCELLED = 0
INITIAL = 0
LIMIT = 3

class State:
    def __init__(self):
        self.logger = logging.getLogger(os.path.basename(__file__))

    def handle_data(self, rainrate):
        assert 0, "run not implemented"
    def handle_timeout(self):
        assert 0, "run not implemented"
    def get_timeout( self ):
        assert 0, "run not implemented"
    def next(self):
        assert 0, "next not implemented"
    def get_message(self):
        assert 0, "next not implemented"
    def enter(self):
        pass
    def exit(self):
        pass


class StateMachine():
    def __init__(self, config, initialState):
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__.__name__
        self.logger = logging.getLogger(the_class)
        self.currentState = initialState
        self.config = config
    
    def get_timeout(self):
        return self.currentState.get_timeout()

    def handle_timeout(self):
        return self.currentState.handle_timeout()

    def handle_data(self, value):
        '''
        Pass data to current state
        '''
        return self.currentState.handle_data(value)

    def next(self):
        '''
        Return the next state
        '''
        return self.currentState.next()
    
    def change_state(self, new_state):
        '''
        Change to new state
        '''
        self.logger.info("["+self.currentState.__class__.__name__+"] --> ["+ str(new_state.__class__.__name__)+"]")
        self.currentState.exit()
        self.currentState = new_state
        self.currentState.enter()
        msg = new_state.get_message()
        if msg:
           helper.send_telegram_message(self.config, msg)

