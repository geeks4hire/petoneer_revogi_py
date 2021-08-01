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

    API_URL                         = "https://as.revogi.net/app"

    API_LOGIN_PATH                  = "/user/101"
    API_DEVICE_LIST_PATH            = "/user/500"
    API_DEVICE_DETAILS_PATH         = "/pww/31101"
    API_DEVICE_SWITCH_PATH          = "/pww/21101"
    API_DEVICE_LED_PATH             = "/pww/21104"
    API_RESET_CLEAN_PUMP_TIMER      = "/pww/21103"
    API_RESET_FILTER_CHANGE_TIMER    = "/pww/21105"
    API_RESET_WATER_CHANGE_TIMER    = "/pww/21107"

    SECONDS_FOUNTAIN_WATER_CHANGE   = 5 * 24 * 60 * 60
    SECONDS_FOUNTAIN_FILTER_CHANGE  = 30 * 24 * 60 * 60
    SECONDS_FOUNTAIN_CLEAN_PUMP     = 60 * 24 * 60 * 60 
    
    Debug                           = 1 

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
            headers = { 
                "accessToken": self._auth_token 
            }
        else:
            headers = {}

        # Make the request
        try:
            resp = requests.post(self._url(path), json=payload, headers=headers)
            return resp

        except Exception as e:
            raise PetoneerApiServerOffline(self._url(path), 501, 'Unable to connect to Petoneer API server - Connection Failed')
            #raise PetoneerServerError(501, self._url(path), e.__cause__, 'Unable to connect to Petoneer API server - Connection Failed')

    def _url(self, path):        
        return self.API_URL + path

    def _numOfDaysRemaining(self, device_current_time_unix_timestamp: int, device_feature_unix_timestamp: int, threshold_interval_secs):
        date1 = datetime.fromtimestamp(device_feature_unix_timestamp)
        date2 = datetime.fromtimestamp(device_current_time_unix_timestamp)

        seconds_difference = (date2 - date1).total_seconds()
        days_remaining = math.ceil((threshold_interval_secs - seconds_difference)/60/60/24)

        return days_remaining

    def _percentageRemaining(self, device_current_time_unix_timestamp: int, device_feature_unix_timestamp: int, threshold_interval_secs):
        date1 = datetime.fromtimestamp(device_feature_unix_timestamp)
        date2 = datetime.fromtimestamp(device_current_time_unix_timestamp)

        seconds_difference = (date2 - date1).total_seconds()
        percent_remaining = round(((threshold_interval_secs - seconds_difference) / threshold_interval_secs) * 100)

        return percent_remaining

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
            0: "Empty",
            1: "Low",
            2: "Adequate",
            3: "Good",
            4: "Full"
        }
        return (level_labels.get(level_int, 'Invalid Water Level Value!'))

    def _waterPercentage(self, level_int):
        percent_labels={
            0: "0%",
            1: "25%",
            2: "50%",
            3: "75%",
            4: "100%"
        }
        return (percent_labels.get(level_int, 'Invalid Water Level Value!'))

    def _pumpStatus(self, switch_int):
        pump_statuses={
            0: "Off",
            1: "On"
        }
        return (pump_statuses.get(switch_int, 'Invalid Pump Switch Value!'))

    def _tdsLevel(self, tds_level_int):
        if (tds_level_int < 1):
            return "Invalid TDS Level Provided!"
        elif (tds_level_int <= 50):
            return "Excellent"
        elif (tds_level_int <= 100):
            return "Drinkable"
        else:
            return "Undrinkable"

    def auth(self, username, password, country="AU", timezone="Australia/Sydney"):
        if (username == ""):           
            raise PetoneerInvalidArgument('auth', 'username', 'Username cannot be blank')

        if (password == ""):
            raise PetoneerInvalidArgument('auth', 'password', 'Password cannot be blank')

        if (country == ""):
            raise PetoneerInvalidArgument('auth', 'country', 'Country code cannot be blank')

        if (timezone == ""):
            raise PetoneerInvalidArgument('auth', 'timezone', 'Timezone cannot be blank')

        # Build the authentication request payload
        auth_payload = {
          "language": "0",
          "type": 2,
          "region": {
            "country": country,
            "timezone": timezone
          },
          "username": username,
          "password": password
        }
        
        if (self.Debug):
            print(f"Authenticating to {self.API_URL} as {username}...")

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
                    raise PetoneerAuthenticationError(resp.status_code, username, resp.text, 'Unable to authenticate with Petoneer API - Incorrect username or password?')
            else:
                raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Error from Server while authenticating user - Unexpected server response')
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Error from Server while authenticating user - Unknown Error')

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
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to obtain list of Petoneer Fountain devices - Server Error')

    def get_device_details(self, device_code):
        if (device_code == ""):
            raise PetoneerInvalidArgument('get_device_details', 'device_code', 'The device serial number must be provided')

        if (self.Debug):
            print(f"Getting details for device {device_code}")

        payload = { 
            "sn": device_code, 
            "protocol": "3" 
        }

        resp = self._req(self.API_DEVICE_DETAILS_PATH, payload)

        if(resp.status_code == 200):
            json_resp = resp.json()

            if (json_resp['code'] == 200):
                device_details = json_resp['data']
                device_details['waterLevel'] = [
                    f"{self._waterPercentage(device_details['level'])}",
                    f"{self._waterLevel(device_details['level'])}"
                ]
                device_details['waterQuality'] = self._tdsLevel(device_details['tds'])
                device_details['changeFilter'] = [
                    f"{self._numOfDaysRemaining(device_details['time'], device_details['filtertime'], self.SECONDS_FOUNTAIN_FILTER_CHANGE)} days",
                    f"{self._percentageRemaining(device_details['time'], device_details['filtertime'], self.SECONDS_FOUNTAIN_FILTER_CHANGE)} %"
                ]
                device_details['changeWater'] = [
                    f"{self._numOfDaysRemaining(device_details['time'], device_details['watertime'], self.SECONDS_FOUNTAIN_WATER_CHANGE)} days",
                    f"{self._percentageRemaining(device_details['time'], device_details['watertime'], self.SECONDS_FOUNTAIN_WATER_CHANGE)} %"
                ]
                device_details['cleanPump'] = [ 
                    f"{self._numOfDaysRemaining(device_details['time'], device_details['motortime'], self.SECONDS_FOUNTAIN_CLEAN_PUMP)} days",
                    f"{self._percentageRemaining(device_details['time'], device_details['motortime'], self.SECONDS_FOUNTAIN_CLEAN_PUMP)} %"
                ]
                if 'section' in device_details:
                    device_details['ledsDimmingSchedule'] = [
                        self._scheduleValueToDateTime(device_details['section'][0]).strftime('%H:%M:%S'),
                        self._scheduleValueToDateTime(device_details['section'][1]).strftime('%H:%M:%S')
                    ]
                device_details['ledsStatus'] = self._ledStatus(device_details['led'], device_details['ledmode'], device_details['section'][0], device_details['section'][1])
                device_details['pumpStatus'] = self._pumpStatus(device_details['switch'])

                return device_details
            else:
                raise PetoneerInvalidServerResponse(resp.http_code, resp.url, resp.text, 'Unable to obtain Petoneer Fountain device details - Unexpected Server Response')
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to obtain Petoneer Fountain device details - Server Error')

    def turn_on(self, device_code):
        if (device_code == ""):
            raise PetoneerInvalidArgument('turn_on', 'device_code', 'The device serial number must be provided')

        payload = { 
            "sn": device_code, 
            "protocol": "3", 
            "switch": 1 
        }

        resp = self._req(self.API_DEVICE_SWITCH_PATH, payload)

        if (resp.status_code == 200): 
            json_resp = resp.json()

            device_details = json_resp['data']
            return device_details
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to switch on Petoneer Fountain - Server Error')

    def turn_off(self, device_code):
        if (device_code == ""):
            raise PetoneerInvalidArgument('turn_off', 'device_code', 'The device serial number must be provided')

        payload = {
            "sn": device_code, 
            "protocol": "3", 
            "switch": 0 
        }

        resp = self._req(self.API_DEVICE_SWITCH_PATH, payload)

        if (resp.status_code == 200):
            json_resp = resp.json()

            device_details = json_resp['data']
            return device_details
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to switch off Petoneer Fountain - Server Error')

    def turn_led_on(self, device_code, leds_dimmed = False):
        if (device_code == ""):
            raise PetoneerInvalidArgument('turn_led_on', 'device_code', 'The device serial number must be provided')

        if (leds_dimmed):
            # create payload with LED dimming schedule that spans from 00:00 to 23:59hrs
            payload = { 
                "sn": device_code, 
                "protocol": "3", 
                "ledmode": 1, 
                "section": [0, 1439], 
                "led": 1 
            }
            # create a payload with no scheduled times for LED dimming
        else:
            payload = { 
                "sn": device_code, 
                "protocol": "3", 
                "ledmode": 1, 
                "section": [0, 0], 
                "led": 1 
            }
        
        resp = self._req(self.API_DEVICE_LED_PATH, payload)

        if (resp.status_code == 200):
            json_resp = resp.json()

            device_details = json_resp['data']
            return device_details
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to switch on Petoneer Fountain LEDs - Server Error')

    def turn_led_off(self, device_code):
        if (device_code == ""):
            raise PetoneerInvalidArgument('turn_led_off', 'device_code', 'The device serial number must be provided') 

        payload = {         
            "sn": device_code, 
            "ledmode": 0, 
            "section": [0,1439], 
            "protocol": "3", 
            "led": 0 
        }

        resp = self._req(self.API_DEVICE_LED_PATH, payload)

        if (resp.status_code == 200):
            json_resp = resp.json()

            device_details = json_resp['data']
            return device_details
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to switch off Petoneer Fountain LEDs - Server Error')

    def reset_filter_change_timer(self, device_code):
        if (device_code == ""):
            raise PetoneerInvalidArgument('reset_filter_change_timer', 'device_code', 'The device serial number must be provided') 

        payload = {         
            "sn": device_code, 
            "protocol": "3"
        }

        resp = self._req(self.API_RESET_FILTER_CHANGE_TIMER, payload)

        if (resp.status_code == 200):
            json_resp = resp.json()

            device_details = json_resp['data']
            return device_details
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to reset the "filter change" countdown timer on Petoneer Fountain - Server Error')

    def reset_water_change_timer(self, device_code):
        if (device_code == ""):
            raise PetoneerInvalidArgument('reset_water_change_timer', 'device_code', 'The device serial number must be provided') 

        payload = {         
            "sn": device_code, 
            "protocol": "3"
        }

        resp = self._req(self.API_RESET_WATER_CHANGE_TIMER, payload)

        if (resp.status_code == 200):
            json_resp = resp.json()

            device_details = json_resp['data']
            return device_details
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to reset the "water changeover" countdown timer on Petoneer Fountain - Server Error')

    def reset_clean_pump_timer(self, device_code):
        if (device_code == ""):
            raise PetoneerInvalidArgument('reset_clean_pump_timer', 'device_code', 'The device serial number must be provided') 

        payload = {         
            "sn": device_code, 
            "protocol": "3"
        }

        resp = self._req(self.API_RESET_CLEAN_PUMP_TIMER, payload)

        if (resp.status_code == 200):
            json_resp = resp.json()

            device_details = json_resp['data']
            return device_details
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to reset the "pump clean" countdown timer on Petoneer Fountain - Server Error')