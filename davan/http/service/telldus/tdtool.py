#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, getopt, http.client, urllib.request, urllib.parse, urllib.error, json, os
import oauth.oauth as oauth
import datetime
from configobj import ConfigObj
import logging 

global logger
logger = logging.getLogger(os.path.basename(__file__))
import davan.util.application_logger as log_manager
#insert your own public_key and private_key
import davan.config.config_creator as config_creator
configuration = config_creator.create()
PUBLIC_KEY = configuration["TELLDUS_PUBLIC_KEY"]
PRIVATE_KEY = configuration["TELLDUS_PRIVATE_KEY"]

TELLSTICK_TURNON = 1
TELLSTICK_TURNOFF = 2
TELLSTICK_BELL = 4
TELLSTICK_DIM = 16
TELLSTICK_UP = 128
TELLSTICK_DOWN = 256

SUPPORTED_METHODS = TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_BELL | TELLSTICK_DIM | TELLSTICK_UP | TELLSTICK_DOWN;

def printUsage():
	print(("Usage: %s [ options ]" % sys.argv[0]))
	print("")
	print("Options:")
	print("         -[lnfdbvh] [ --list ] [ --help ]")
	print("                      [ --on device ] [ --off device ] [ --bell device ]")
	print("                      [ --dimlevel level --dim device ]")
	print("                      [ --up device --down device ]")
	print("")
	print("       --list (-l short option)")
	print("             List currently configured devices.")
	print("")
	print("       --help (-h short option)")
	print("             Shows this screen.")
	print("")
	print("       --on device (-n short option)")
	print("             Turns on device. 'device' must be an integer of the device-id")
	print("             Device-id and name is outputed with the --list option")
	print("")
	print("       --off device (-f short option)")
	print("             Turns off device. 'device' must be an integer of the device-id")
	print("             Device-id and name is outputed with the --list option")
	print("")
	print("       --dim device (-d short option)")
	print("             Dims device. 'device' must be an integer of the device-id")
	print("             Device-id and name is outputed with the --list option")
	print("             Note: The dimlevel parameter must be set before using this option.")
	print("")
	print("       --dimlevel level (-v short option)")
	print("             Set dim level. 'level' should an integer, 0-255.")
	print("             Note: This parameter must be set before using dim.")
	print("")
	print("       --bell device (-b short option)")
	print("             Sends bell command to devices supporting this. 'device' must")
	print("             be an integer of the device-id")
	print("             Device-id and name is outputed with the --list option")
	print("")
	print("       --up device")
	print("             Sends up command to devices supporting this. 'device' must")
	print("             be an integer of the device-id")
	print("             Device-id and name is outputed with the --list option")
	print("")
	print("       --down device")
	print("             Sends down command to devices supporting this. 'device' must")
	print("             be an integer of the device-id")
	print("             Device-id and name is outputed with the --list option")
	print("")
	print("       --list-sensors (-s short option)")
	print("             Lists currently configured sensors")
	print("")
	print("       --sensor-data sensor (-d short option)")
	print("             Get sensor data with sensor id number")
	print("")
	print("Report bugs to <info.tech@telldus.se>")

def listSensors():
	response = doRequest('sensors/list', {'includeIgnored': 1});
	logger.debug("Number of sensors: %i" % len(response['sensor']));
	for sensor in response['sensor']:
		lastupdate = datetime.datetime.fromtimestamp(int(sensor['lastUpdated']));
		logger.debug( "%s\t%s\t%s" % (sensor['id'], sensor['name'], lastupdate))


def listSensorsAndValues():
	response = doRequest('sensors/list', {'includeValues': 1});
	return response

def listDevicesAndValues():
	response = doRequest('devices/list', {'supportedMethods': SUPPORTED_METHODS})
	return response

def getSensorData(sensorId):
	response = doRequest('sensor/info', {'id': sensorId });
	lastupdate = datetime.datetime.fromtimestamp(int(response['lastUpdated']));
	sensor_name = response['name'];
	for data in response['data']:
		logger.debug( "%s\t%s\t%s\t%s" % (sensor_name, data['name'], data['value'], lastupdate)	)

def listDevices():
	response = doRequest('devices/list', {'supportedMethods': SUPPORTED_METHODS})
	logger.debug("Number of devices: %i" % len(response['device']));
	for device in response['device']:
		if (device['state'] == TELLSTICK_TURNON):
			state = 'ON'
		elif (device['state'] == TELLSTICK_TURNOFF):
			state = 'OFF'
		elif (device['state'] == TELLSTICK_DIM):
			state = "DIMMED"
		elif (device['state'] == TELLSTICK_UP):
			state = "UP"
		elif (device['state'] == TELLSTICK_DOWN):
			state = "DOWN"
		else:
			state = 'Unknown state'

		logger.debug("%s\t%s\t%s" % (device['id'], device['name'], state));

def doMethod(deviceId, methodId, methodValue = 0):
	response = doRequest('device/info', {'id': deviceId})

	if (methodId == TELLSTICK_TURNON):
		method = 'on'
	elif (methodId == TELLSTICK_TURNOFF):
		method = 'off'
	elif (methodId == TELLSTICK_BELL):
		method = 'bell'
	elif (methodId == TELLSTICK_UP):
		method = 'up'
	elif (methodId == TELLSTICK_DOWN):
		method = 'down'

	if ('error' in response):
		name = ''
		retString = response['error']
	else:
		name = response['name']
		response = doRequest('device/command', {'id': deviceId, 'method': methodId, 'value': methodValue})
		if ('error' in response):
			retString = response['error']
		else:
			retString = response['status']

	if (methodId in (TELLSTICK_TURNON, TELLSTICK_TURNOFF)):
		logger.debug("Turning %s device %s, %s - %s" % ( method, deviceId, name, retString));
	elif (methodId in (TELLSTICK_BELL, TELLSTICK_UP, TELLSTICK_DOWN)):
		logger.debug("Sending %s to: %s %s - %s" % (method, deviceId, name, retString))
	elif (methodId == TELLSTICK_DIM):
		logger.debug("Dimming device: %s %s to %s - %s" % (deviceId, name, methodValue, retString))


def doRequest(method, params):
	global config
	config = ConfigObj(os.environ['HOME'] + '/.config/Telldus/tdtool.conf')

	consumer = oauth.OAuthConsumer(PUBLIC_KEY, PRIVATE_KEY)
	token = oauth.OAuthToken(config['token'], config['tokenSecret'])

	oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, http_method='GET', http_url="http://api.telldus.com/json/" + method, parameters=params)
	oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
	headers = oauth_request.to_header()
	headers['Content-Type'] = 'application/x-www-form-urlencoded'

	conn = http.client.HTTPConnection("api.telldus.com:80")
	conn.request('GET', "/json/" + method + "?" + urllib.parse.urlencode(params, True).replace('+', '%20'), headers=headers)

	response = conn.getresponse()
	try:	
		return json.load(response)
	except:
		logger.debug( 'Failed to decode response :%s'%str(response))
		return ""

def requestToken():
	global config
	consumer = oauth.OAuthConsumer(PUBLIC_KEY, PRIVATE_KEY)
	request = oauth.OAuthRequest.from_consumer_and_token(consumer, http_url='http://api.telldus.com/oauth/requestToken')
	request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, None)
	conn = http.client.HTTPConnection('api.telldus.com:80')
	conn.request(request.http_method, '/oauth/requestToken', headers=request.to_header())

	resp = conn.getresponse().read()
	token = oauth.OAuthToken.from_string(resp)
	logger.debug( 'Open the following url in your webbrowser:\nhttp://api.telldus.com/oauth/authorize?oauth_token=%s\n' % token.key)
	logger.debug( 'After logging in and accepting to use this application run:\n%s --authenticate' % (sys.argv[0]))
	config['requestToken'] = str(token.key)
	config['requestTokenSecret'] = str(token.secret)
	saveConfig()

def getAccessToken():
	global config
	consumer = oauth.OAuthConsumer(PUBLIC_KEY, PRIVATE_KEY)
	token = oauth.OAuthToken(config['requestToken'], config['requestTokenSecret'])
	request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, http_method='GET', http_url='http://api.telldus.com/oauth/accessToken')
	request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
	conn = http.client.HTTPConnection('api.telldus.com:80')
	conn.request(request.http_method, request.to_url(), headers=request.to_header())

	resp = conn.getresponse()
	if resp.status != 200:
		logger.debug( 'Error retreiving access token, the server replied:\n%s' % resp.read())
		return
	token = oauth.OAuthToken.from_string(resp.read())
	config['requestToken'] = None
	config['requestTokenSecret'] = None
	config['token'] = str(token.key)
	config['tokenSecret'] = str(token.secret)
	logger.debug( 'Authentication successful, you can now use tdtool')
	saveConfig()

def authenticate():
	try:
		opts, args = getopt.getopt(sys.argv[1:], '', ['authenticate'])
		for opt, arg in opts:
			if opt in ('--authenticate'):
				getAccessToken()
				return
	except getopt.GetoptError:
		pass
	requestToken()

def saveConfig():
	global config
	try:
		os.makedirs(os.environ['HOME'] + '/.config/Telldus')
	except:
		pass
	config.write()

def main(argv):
	global config
	if ('token' not in config or config['token'] == ''):
		authenticate()
		return
	try:
		opts, args = getopt.getopt(argv, "lsd:n:f:d:b:v:h", ["list", "list-sensors", "sensor-data=", "on=", "off=", "dim=", "bell=", "dimlevel=", "up=", "down=", "help"])
	except getopt.GetoptError:
		printUsage()
		sys.exit(2)

	dimlevel = -1

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			printUsage()

		elif opt in ("-l", "--list"):
			listDevices()

		elif opt in ("-s", "--list-sensors"):
			listSensors()

		elif opt in ("-x", "--list-sensorsvalue"):
			listSensorsAndValues()

		elif opt in ("-d", "--sensor-data"):
			getSensorData(arg)

		elif opt in ("-n", "--on"):
			doMethod(arg, TELLSTICK_TURNON)

		elif opt in ("-f", "--off"):
			doMethod(arg, TELLSTICK_TURNOFF)

		elif opt in ("-b", "--bell"):
			doMethod(arg, TELLSTICK_BELL)

		elif opt in ("-d", "--dim"):
			if (dimlevel < 0):
				logger.debug("Dimlevel must be set with --dimlevel before --dim")
			else:
				doMethod(arg, TELLSTICK_DIM, dimlevel)

		elif opt in ("-v", "--dimlevel"):
			dimlevel = arg

		elif opt in ("--up"):
			doMethod(arg, TELLSTICK_UP)

		elif opt in ("--down"):
			doMethod(arg, TELLSTICK_DOWN)

if __name__ == "__main__":
	config = ConfigObj(os.environ['HOME'] + '/.config/Telldus/tdtool.conf')
	configuration = config_creator.create()
	log_manager.start_logging(configuration["LOGFILE_PATH"],loglevel=4)
	main(sys.argv[1:])
