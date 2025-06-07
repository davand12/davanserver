import logging
import os
import http.client
import requests

import time
import davan.util.constants as constants

import davan.config.config_creator as configuration
headers = {'content-type': 'text/xml;charset="utf-8"'}
url = "http://127.0.0.1:8080/ImouCameraService"
human_detection = '{"deviceType":"IPC","msgType":"human","cname":"Framsidan","labelType":"humanAlarm","remark":"","zerotime":1690828798,"type":120,"userId":"23378547","token":"be96a09e65af46c69eba6a119f32ac9b_big","accessType":"PaaS","picUrl":["https://imou-fk3-ali-online-paas-private-picture.oss-eu-central-1.aliyuncs.com/8C0577BAAZ85EA7_img/Alarm/0/be96a09e65af46c69eba6a119f32ac9b_big_0_thumb_qcif.dav?Expires=1690915196&OSSAccessKeyId=LTAI5tLLa1JsJgrk5z56iFRB&Signature=pAy7pQaINS8Ty%2FzkLUsFUrsB2dI%3D"],"utcTime":1690828798,"appId":"lcfb0ddc13ada74f5a","action":"start","dname":"Framsidan","id":1644865862852656,"time":1690835998,"thumbUrl":"https://imou-fk3-ali-online-paas-private-picture.oss-eu-central-1.aliyuncs.com/8C0577BAAZ85EA7_img/Alarm/0/be96a09e65af46c69eba6a119f32ac9b_big_0_thumb_qcif.dav?Expires=1690915196&OSSAccessKeyId=LTAI5tLLa1JsJgrk5z56iFRB&Signature=pAy7pQaINS8Ty%2FzkLUsFUrsB2dI%3D","did":"8C0577BAAZ85EA7","cid":0}'
activate_camera = '{"msgType":"openCamera","cname":"Framsidan","remark":"","zerotime":1690828798,"type":152,"userId":"23378547","utcTime":1690828798,"appId":"lcfb0ddc13ada74f5a","dname":"Framsidan","time":1690835998,"did":"8C0577BAAZ85EA7","cid":0}'
unknown_camera = '{"msgType":"openCamera","cname":"MyCamera","remark":"","zerotime":1690828798,"type":152,"userId":"23378547","utcTime":1690828798,"appId":"lcfb0ddc13ada74f5a","dname":"Framsidan","time":1690835998,"did":"8C0577BAAZ85EA7","cid":0}'
sleep = '{"deviceType":"IPC","msgType":"sleep","cname":"Framsidan","remark":"","zerotime":1690828809,"type":168,"userId":"23378547","accessType":"","localTime":"","utcTime":1690828809,"appId":"lcfb0ddc13ada74f5a","dname":"Framsidan","time":1690828809,"did":"8C0577BAAZ85EA7","cid":-1,"desc":{"status":"sleep"}'
class Test_ImouCameraService():
    def __init__(self):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.conn = http.client.HTTPConnection(config["SERVER_ADRESS"] + ":" + str(config["SERVER_PORT"]))

    def test_human_detected(self):
        self.logger.info("Starting test test_human_detected")
        self.send_request(human_detection)

    def test_activate_camera(self):
        self.logger.info("Starting test test_activate_camera")
        self.send_request(activate_camera)

    def test_unknown_camera(self):
        self.logger.info("Starting test test_unknown_camera")
        self.send_request(unknown_camera)

    def test_sleep_camera(self):
        self.logger.info("Starting test test_sleep_camera")
        self.send_request(sleep)

    def send_request(self, body):
        self.logger.info("Send request " + body)
        r = requests.post(url,data=body,headers=headers)
        self.logger.debug("Received response [" + str(r.status_code) +"]")

if __name__ == '__main__':
    from davan.util import application_logger as log_config

    config = configuration.create()
    log_config.start_logging(config['LOGFILE_PATH'],loglevel=4)
    
    test = Test_ImouCameraService()
    test.test_activate_camera()
    time.sleep(10)
    test.test_human_detected()
    time.sleep(10)
    test.test_unknown_camera()
    time.sleep(10)
    test.test_sleep_camera()
    #test.test_active_2_charging()
    #test.test_charging_to_working()
    #test.test_working_to_working()
