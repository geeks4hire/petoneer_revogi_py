"""
Python module to get device details from Petoneer / Revogi equipment
Tested with a Petoneer Fresco Pro water fountain
"""

from datetime import time, date, datetime
import logging
import urllib.parse
import math

import requests
import json
import hashlib

from petoneerErrors import *

from pprint import pprint

class Petoneer:
    """
    Class to interface with the cloud-based API for the Revogi Smart Home equipment
    """

    API_URL                 = "https://as.revogi.net/app"

    API_LOGIN_PATH          = "/user/101"
    API_DEVICE_LIST_PATH    = "/user/500"
    API_DEVICE_DETAILS_PATH = "/pww/31101"
    API_DEVICE_SWITCH_PATH  = "/pww/21101"
    API_DEVICE_LED_PATH     = "/pww/21104"
    
    Debug                   = 1 

    def __init__(self):
        # Nothing to do here
        if (self.Debug):
            print("Petoneer Python API via the Dark Arts")
            print("====================================")
            print("")

    def _debug(self, msg):
        print(msg)
        #pass

        return

    def _req(self, path, payload, auth=True):
        if (auth):
            headers = { "accessToken": self._auth_token }
        else:
            headers = {}

        # Make the request
        resp = requests.post(self._url(path), json=payload, headers=headers)
        return resp

    def _url(self, path):        
        return self.API_URL + path

    def _numOfDays(self, date1_unix_timestamp: int, date2_unix_timestamp: int):
        date1 = datetime.fromtimestamp(date1_unix_timestamp)
        date2 = datetime.fromtimestamp(date2_unix_timestamp)

        seconds_difference = (date2 - date1).total_seconds()
        hours_difference = int((date2 - date1).seconds / 60)

        return seconds_difference

    def _dateTimeToScheduleValue(self, schedule_time: datetime):
        schedule_value = (schedule_time.hour * 60) + schedule_time.min
        return schedule_value

    def _scheduleValueToDateTime(self, schedule_time_str):
        if (schedule_time_str == 0):
            return time(0,0,0)

        hours = math.floor(int(schedule_time_str) / 60)
        mins =  int(schedule_time_str - (hours * 60))

        if (hours <= 23) and (hours >= 0) and (mins <=59) and (mins >= 0):
            return time(hours, mins, 0)
        else:
            return time(0,0,0)            

    def _ledStatus(self, led_value: int, ledmode_value: int, schedule_value1: int = 0, schedule_value2: int = 0):
        if (schedule_value2 != schedule_value1) and (schedule_value1 >=0) and (schedule_value1 <= 1439) and (schedule_value2 >= 0) and (schedule_value2 <= 1439):
            sched_start = self._scheduleValueToDateTime(schedule_value1)
            sched_end = self._scheduleValueToDateTime(schedule_value2)
            current_time = datetime.now().time()
            
            if ((sched_start < current_time) and (sched_end > current_time)):
                ledIntensity = "Dimmed"
            else:
                ledIntensity = "On"
        else:
            ledIntensity = "On"

        if ((led_value == 1) or (ledmode_value == 10)):
            return ledIntensity
        else:
            return "Off"

    def _waterLevel(self, level_int):
        level_labels={
            0: "0% - Empty",
            1: "25% - Low",
            2: "50% - Adequate",
            3: "75% - Good",
            4: "100% - Full"
        }
        return (level_labels.get(level_int, "Invalid Water Level Value!"))
    
    def _pumpStatus(self, switch_int):
        pump_statuses={
            0: "Off",
            1: "On"
        }
        return (pump_statuses.get(switch_int, "Invalid Pump Switch Value!"))

    def _tdsLevel(self, tds_level_int):
        if tds_level_int < 1:
            return "Invalid TDS Level Provided!"
        elif tds_level_int < 50:
            return "Excellent"
        elif tds_level_int < 100:
            return "Drinkable"
        else:
            return "Undrinkable"

    def auth(self, username, password):
        # Build the authentication request payload
        auth_payload = {
          "language": "0",
          "type": 2,
          "region": {
            "country": "AU",
            "timezone": "Australia/Sydney"
          },
          "username": username,
          "password": password
        }
        
        if (self.Debug):
            print("Authenticating to " + self.API_URL + " as " + username + "...")

        #
        # Attempt to authenticate - if successful, we will get an HTTP 200
        # response back which will include our authentication token that
        # we need to use for subsequent requests.
        #
        resp = self._req(self.API_LOGIN_PATH, auth_payload, auth=False)
        if (resp.status_code == 200):
            json_resp = resp.json()

            if ('data' in json_resp):
                # Verify we have an auth token in the response - if so, store it
                if ('accessToken' in json_resp['data']):
                    self._auth_token = json_resp['data']['accessToken']
                    if (self.Debug):
                        print("Authentication successful - token ***" + self._auth_token[-4:])
                else:
                    raise ConnectionAbortedError('auth() failed - HTTP {}:  {}'.format(resp.status_code, json_resp['msg']))    
            else:
                raise ConnectionAbortedError('auth() failed - HTTP {}: {}'.format(resp.status_code, resp.raw))
        else:
            raise ConnectionAbortedError('auth() failed - HTTP {}: {}'.format(resp.status_code, resp.raw))

    def get_registered_devices(self):
        if (self.Debug):
            print("Getting All Devices")
        payload = {
          "dev": "all",
          "protocol": "3"
        }
        resp = self._req(self.API_DEVICE_LIST_PATH, payload)
        if (resp.status_code == 200):
            json_resp = resp.json()

            if 'data' in json_resp:
                devices =  json_resp['data']['dev']
            else:
                devices = None

            # Return the list of devices
            return devices
        else:
            raise ConnectionAbortedError('get_registered_devices() failed - server status code: {}\n{}'.format(resp.status_code, resp.raw))

    def get_device_details(self, device_code):
        if (self.Debug):
            print("Getting details for device " + device_code)
        payload = { "sn": device_code, "protocol": "3" }
        resp = self._req(self.API_DEVICE_DETAILS_PATH, payload)
        if(resp.status_code == 200):
            json_resp = resp.json()

            if (json_resp['code'] == 200):
                device_details = json_resp['data']
                device_details['waterLevel'] = self._waterLevel(device_details['level'])
                device_details['waterQuality'] = self._tdsLevel(device_details['tds'])
                #device_details['waterFilterDays'] = self._numOfDays(device_details['time'], device_details['filtertime'])
    
                if 'section' in device_details:
                    device_details['schedStart'] = self._scheduleValueToDateTime(device_details['section'][0]).strftime('%H:%M:%S')
                    device_details['schedEnd'] = self._scheduleValueToDateTime(device_details['section'][1]).strftime('%H:%M:%S')

                device_details['ledsStatus'] = self._ledStatus(device_details['led'], device_details['ledmode'], device_details['section'][0], device_details['section'][1])
                device_details['pumpStatus'] = self._pumpStatus(device_details['switch'])

                return device_details
            else:
                raise ConnectionAbortedError('get_device_details() failed - server response: \n{}'.format(resp.raw))                
        else:
            raise ConnectionAbortedError('get_device_details() failed - server status code: {}\n{}'.format(resp.status_code, resp.raw))

    def turn_on(self, device_code):
        payload = { "sn": device_code, "protocol": "3", "switch": 1 }
        resp = self._req(self.API_DEVICE_SWITCH_PATH, payload)
        if (resp.status_code == 200):
            json_resp = resp.json()

            device_details = json_resp['data']
            return device_details
        else:
            raise ConnectionAbortedError('turn_on() failed - server status code: {}\n{}'.format(resp.status_code, resp.raw))

    def turn_off(self, device_code):
        payload = { "sn": device_code, "protocol": "3", "switch": 0 }
        resp = self._req(self.API_DEVICE_SWITCH_PATH, payload)
        if (resp.status_code == 200):
            json_resp = resp.json()

            device_details = json_resp['data']
            return device_details
        else:
            raise ConnectionAbortedError('turn_off() failed - server status code: {}\n{}'.format(resp.status_code, resp.raw))

    def turn_led_on(self, device_code, leds_dimmed = False):
        if (leds_dimmed): 
            payload = { "sn": device_code, "protocol": "3", "ledmode": 1, "section": [0, 1439], "led": 1 }
        else:
            payload = { "sn": device_code, "protocol": "3", "ledmode": 1, "section": [0, 0], "led": 1 }
        
        resp = self._req(self.API_DEVICE_LED_PATH, payload)
        if (resp.status_code == 200):
            json_resp = resp.json()

            device_details = json_resp['data']
            return device_details
        else:
            raise ConnectionAbortedError('turn_led_off() failed - server status code: {}\n{}'.format(resp.status_code, resp.raw))

    def turn_led_off(self, device_code):
        payload = { "sn": device_code, "ledmode": 0, "section": [0,1439], "protocol": "3", "led": "0" }
        resp = self._req(self.API_DEVICE_LED_PATH, payload)
        if (resp.status_code == 200):
            json_resp = resp.json()

            device_details = json_resp['data']
            return device_details
        else:
            raise ConnectionAbortedError('turn_led_off() failed - server status code: {}\n{}'.format(resp.status_code, resp.raw))
