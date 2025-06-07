import json
import logging
import time
import os
import traceback


import requests
from davan.http.service.smartlife.TuyaLight import TuyaLight

REFRESHTIME = 60 * 60 * 12
TUYACLOUDURL = "https://px1.tuya{}.com"
DEFAULTREGION = "eu"
_LOGGER = logging.getLogger(os.path.basename(__file__))


class TuyaSession:

    username = ""
    password = ""
    countryCode = ""
    bizType = ""
    accessToken = ""
    refreshToken = ""
    expireTime = 0
    devices = []
    region = DEFAULTREGION


def get_access_token(session):
    response = requests.post(
        (TUYACLOUDURL + "/homeassistant/auth.do").format(session.region),
        data={
            "userName": session.username,
            "password": session.password,
            "countryCode": session.countryCode,
            "bizType": session.bizType,
            "from": "tuya",
        },
    )
    response_json = response.json()
    if response_json.get("responseStatus") == "error":
        message = response_json.get("errorMsg")
        if message == "error":
            raise TuyaAPIException("get access token failed")
        else:
            raise TuyaAPIException(message)

    session.accessToken = response_json.get("access_token")
    session.refreshToken = response_json.get("refresh_token")
    session.expireTime = int(time.time()) + response_json.get("expires_in")
    areaCode = session.accessToken[0:2]
    if areaCode == "AY":
        session.region = "cn"
    elif areaCode == "EU":
        session.region = "eu"
    else:
        session.region = "us"

def check_access_token(session):
    if session.username == "" or session.password == "":
        raise TuyaAPIException("can not find username or password")
        return
    if session.accessToken == "" or session.refreshToken == "":
        get_access_token(session)
    elif session.expireTime <= REFRESHTIME + int(time.time()):
        refresh_access_token(session)

def refresh_access_token(session):
    data = "grant_type=refresh_token&refresh_token=" + session.refreshToken
    response = requests.get(
        (TUYACLOUDURL + "/homeassistant/access.do").format(session.region)
        + "?"
        + data
    )
    response_json = response.json()
    if response_json.get("responseStatus") == "error":
        raise TuyaAPIException("refresh token failed")

    session.accessToken = response_json.get("access_token")
    session.refreshToken = response_json.get("refresh_token")
    session.expireTime = int(time.time()) + response_json.get("expires_in")

def poll_devices_update(session):
    check_access_token(session)
    return discover_devices(session)

def discovery(session):
    response = _request(session,"Discovery", "discovery")
    _LOGGER.debug(str(response))

    if response and response["header"]["code"] == "SUCCESS":
        return response["payload"]["devices"]
    return None

def discover_devices(session):
    devices = discovery(session)
    _LOGGER.debug(str(devices))
    
    if not devices:
        return None
    session.devices = []
    for device in devices:
        session.devices.append(TuyaLight(device, session))
    return devices

def get_devices_by_type(session, dev_type):
    device_list = []
    for device in session.devices:
        if device.dev_type() == dev_type:
            device_list.append(device)

def get_all_devices(session):
    return session.devices

def get_device_by_id(session, dev_id):
    for device in session.devices:
        if device.object_id() == dev_id:
            return device
    return None

def get_device_by_name(session, name):
    for device in session.devices:
        if device.name() == name:
            return device

    _LOGGER.debug("Cannot find device: [" + name + "] in  list " + str(session.devices) )
    return None

def device_control(session, devId, action, param=None, namespace="control"):
    if param is None:
        param = {}
    response = _request(session,action, namespace, devId, param)
    if response and response["header"]["code"] == "SUCCESS":
        success = True
    else:
        success = False
    return success, response

def _request(session, name, namespace, devId=None, payload={}):
    header = {"name": name, "namespace": namespace, "payloadVersion": 1}
    payload["accessToken"] = session.accessToken
    if namespace != "discovery":
        payload["devId"] = devId
    data = {"header": header, "payload": payload}
    #logger.info("Req: payload " + str(payload))

    response = requests.post(
        (TUYACLOUDURL + "/homeassistant/skill").format(session.region), json=data
    )
    if not response.ok:
        _LOGGER.warning(
            "request error, status code is %d, device %s",
            response.status_code,
            devId,
        )
        return
    response_json = response.json()
    #logger.info("Response " + str(response_json))
    if response_json["header"]["code"] != "SUCCESS":
        _LOGGER.debug(
            "control device error, error code is " + response_json["header"]["code"]
        )
    return response_json


class TuyaAPIException(Exception):
    pass

