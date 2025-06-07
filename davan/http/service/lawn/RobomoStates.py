import davan.util.constants as constants
import davan.util.helper_functions as helper
from davan.util.StateMachine import StateMachine
from davan.util.StateMachine import State
from datetime import datetime, timedelta

power_level = {
            'Charging':35, # 
            'Working':7,
            'Standby':8,     
            'Off':0.0, 
            'Unknown':-1}


class BaseState(State):
    def __init__(self, service, activity_counter):
        State.__init__( self )
        self.service = service
        self.current_power_level = ""
        self.activity_counter = activity_counter
        self.expire_time = None

    def handle_data(self, value):
        self.service.logger.debug("Data: [" + value+ "]")
        self.current_power_level = float(value)
    
    def get_timeout(self):
        return 60*10 # 10 minutes

    def get_message(self):
        pass
    def enter(self):
        pass
    def exit(self):
        pass
    def handle_timeout(self):
        pass
    

class InactiveState(BaseState):
    def __init__(self, service ):
        BaseState.__init__(self, service, 1)

    def next(self):
        pass

    def enter(self):
        self.service.update_fibaro_device(self.activity_counter, "Inactive" )


class ActiveState(BaseState):
    def __init__(self, service):
        BaseState.__init__(self, service, 1)

    def next(self):
        if self.current_power_level <= power_level["Working"]:
           return WorkingState(self.service, self.activity_counter)
        elif 7.5 <= self.current_power_level <= 30.0:
            return StandbyState(self.service, self.activity_counter)
        elif self.current_power_level > power_level['Charging']:
           return ChargingState(self.service, self.activity_counter)
        else:
           return StandbyState(self.service, self.activity_counter)

    def enter(self):
        self.service.reset_fibaro_device( )


class ChargingState(BaseState):
    def __init__(self, service, activity_counter):
        BaseState.__init__(self, service, activity_counter+1)

    def next(self):
        if self.current_power_level <= power_level["Working"]:
           return WorkingState(self.service, self.activity_counter)
        elif 7.5 <= self.current_power_level <= 30.0:
            return StandbyState(self.service, self.activity_counter)
    
    def get_timeout(self):
        '''
        Expect charging ~2 hours
        '''
        self.expire_time = datetime.now() + timedelta(hours=2)
        return 60*120
    
    def handle_timeout(self):
        if not self.expire_time:
            return

        if datetime.now() > self.expire_time:
            self.service.send_notification("Charging exceeded expected time.")

    def enter(self):
        self.service.update_fibaro_device(self.activity_counter, "Laddar" )


class StandbyState(BaseState):
    def __init__(self, service, activity_counter):
        BaseState.__init__(self, service, activity_counter+1)

    def next(self):
        if self.current_power_level <= power_level["Working"]:
           return WorkingState(self.service, self.activity_counter)
        elif self.current_power_level > power_level['Charging']:
           return ChargingState(self.service, self.activity_counter)

    def enter(self):
        self.service.update_fibaro_device(self.activity_counter, "Standby" )


class WorkingState(BaseState):
    def __init__(self, service, activity_counter):
        BaseState.__init__(self, service, activity_counter+1)

    def next(self):
        if self.current_power_level > power_level['Charging']:
           return ChargingState(self.service, self.activity_counter)
        elif power_level['Working'] < self.current_power_level < power_level['Charging']:
            return StandbyState(self.service, self.activity_counter)

    def get_timeout(self):
        '''
        Expect charging ~2 hours
        '''
        self.expire_time = datetime.now() + timedelta(hours=2)
        return 60*120
    
    def handle_timeout(self):
        if not self.expire_time :
            return 
            
        if datetime.now() > self.expire_time:
            self.service.send_notification("Larry har fastnat, snälla hjälp larry.")

    def enter(self):
        self.service.update_fibaro_device(self.activity_counter, "Klipper" )



class ErrorState(BaseState):
    def __init__(self, service, activity_counter):
        BaseState.__init__(self, service, activity_counter+1)

    def next(self):
        pass 

    def enter(self):
        self.service.update_fibaro_device(self.activity_counter, "Fel" )
