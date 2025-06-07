import logging
import os
import http.client
import time
import davan.util.constants as constants

import davan.config.config_creator as configuration

class Test_RobomowService():
    def __init__(self):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.conn = http.client.HTTPConnection(config["SERVER_ADRESS"] + ":" + str(config["SERVER_PORT"]))

    def test_activate_service(self):
        self.logger.info("Starting test test_activate_service")
        self.send_request("/RobomowService?service="+constants.TURN_ON)

    def test_active_2_charging(self):
        self.logger.info("Starting test test_active_2_charging")
        self.send_request("/RobomowService?service="+constants.TURN_ON)
        time.sleep(900)
        self.send_request("/RobomowService?value=50")
        time.sleep(130)

    def test_charging_to_charging(self):
        self.logger.info("Starting test test_charging_to_working")
        self.send_request("/RobomowService?value=51")
        time.sleep(130)
        self.send_request("/RobomowService?value=5")
        time.sleep(130)

    def test_charging_to_working(self):
        self.logger.info("Starting test test_charging_to_working")
        self.send_request("/RobomowService?value=51")
        time.sleep(130)
        self.send_request("/RobomowService?value=5")
        time.sleep(130)

    def test_working_to_working(self):
        self.logger.info("Starting test test_working_to_working")
        self.send_request("/RobomowService?value=6")
        time.sleep(130)
        self.send_request("/RobomowService?value=4")
        time.sleep(130)

    def send_request(self, message):
        self.logger.info("Send request " + message)
        self.conn.request("GET", message)
        r1 = self.conn.getresponse()
        self.logger.info("Receive response " + str(r1.read()))


if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = Test_RobomowService()
    test.test_activate_service()
    #test.test_active_2_charging()
    #test.test_charging_to_working()
    #test.test_working_to_working()
