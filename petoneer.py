"""
Python module to get device details from Petoneer / Revogi equipment
Tested with a Petoneer Fresco Pro water fountain
"""

import datetime
from datetime import time, date, timedelta
import logging
import urllib.parse
import math

import requests
import json
import hashlib

from petoneerErrors import *
from petoneerHelpers import *
from petoneerConst import *

class Petoneer:
    """
    Class to interface with the cloud-based API for the Revogi Smart Home equipment
    """
    def __init__(self, username="", password="", country="AU", timezone="Australia/Melbourne"):
        self._country_code = country
        self._timezone = timezone
        self._devices_json_collection = None
        
        if (Debug):
            print("Petoneer Python API")
            print("===================")
            print("")

        if((username != None) and (username !="") and
            (password != None) and (password != "")):
            self.authenticate(username, password, country, timezone)
            self.getRegisteredDevices()

    def _debug(self, msg):
        print(msg)
        #pass

        return

    def authenticate(self, username, password, country="AU", timezone="Australia/Melbourne"):
        self._country_code = country
        self._timezone = timezone
    
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
        
        if (Debug):
            print(f"Authenticating to {API_URL} as {username}...")

        #
        # Attempt to authenticate - if successful, we will get an HTTP 200
        # response back which will include our authentication token that
        # we need to use for subsequent requests.
        # 
        resp = PetoneerHelpers.getAPIrequest(API_LOGIN_PATH, auth_payload)

        if (resp.status_code == 200):
            json_resp = resp.json()            

            if ('data' in json_resp):
                # Verify we have an auth token in the response - if so, store it
                if ('accessToken' in json_resp['data']):
                    self._auth_token = json_resp['data']['accessToken']
                    self._auth_token_obtained = datetime.now()
                    self._auth_token_expires = (self._auth_token_obtained + 
                        timedelta(seconds=json_resp['data']['expiresIn']))

                    if (Debug):
                        print("Authentication successful - token ***" + self._auth_token[-4:])

                    # In case this method has been called externally, return the session 
                    # access token.
                    return self._auth_token
                else:
                    raise PetoneerAuthenticationError(resp.status_code, username, resp.text, 'Unable to authenticate with Petoneer API - Incorrect username or password?')
            else:
                raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Error from Server while authenticating user - Unexpected server response')
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Error from Server while authenticating user - Unknown Error')

    def getRegisteredDevices(self):
        if (Debug):
            print("Getting All Devices")
        payload = {
          "dev": "all",
          "protocol": "3"
        }
        
        resp = PetoneerHelpers.getAPIrequest(API_DEVICE_LIST_PATH, payload, self._auth_token)

        if (resp.status_code == 200):
            json_resp = resp.json()

            if (('data' in json_resp) and ('dev' in json_resp['data'])):

                # Update the internally stored collection of device info (JSON)
                self._devices_json_collection = json_resp['data']['dev']

                # Just in case this method was called externally, and not by the
                # init constructor, return the JSON result to caller as well
                return self._devices_json_collection

#
#
# TO-DO:    For each device detailed by Petoneer API as linked to this user account,
#           create an instance of PetoneerFountain (for fountains at least!) automatically.
#           Additionally, if an existing list of devices is being stored, maintain the list
#           if any new devices are added/removed (otherwise just call the "update()" method
#           for each instance of PetoneerFountain.
#
#

            else:
                raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to obtain list of Petoneer Fountain devices - Server Error')
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to obtain list of Petoneer Fountain devices - Server Error')


#
#
# TO-DO: Move all of the below methods over to the PetoneerFountain class, or nest within logical
# PetoneerFountainDetails_XXX sub-classes to perform actions on related statuses etc
#
#

    def turn_on(self, device_code):
        if (device_code == ""):
            raise PetoneerInvalidArgument('turn_on', 'device_code', 'The device serial number must be provided')

        payload = { 
            "sn": device_code, 
            "protocol": "3", 
            "switch": 1 
        }

        resp = PetoneerHelpers.getAPIrequest(API_DEVICE_SWITCH_PATH, payload, self._auth_token)

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

        resp = PetoneerHelpers.getAPIrequest(API_DEVICE_SWITCH_PATH, payload, self._auth_token)

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
        
        resp = PetoneerHelpers.getAPIrequest(API_DEVICE_LED_PATH, payload, self._auth_token)

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

        resp = PetoneerHelpers.getAPIrequest(API_DEVICE_LED_PATH, payload, self._auth_token)

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

        resp = PetoneerHelpers.getAPIrequest(API_RESET_FILTER_CHANGE_TIMER, payload, self._auth_token)

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

        resp = PetoneerHelpers.getAPIrequest(API_RESET_WATER_CHANGE_TIMER, payload, self._auth_token)

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

        resp = PetoneerHelpers.getAPIrequest(API_RESET_CLEAN_PUMP_TIMER, payload, self._auth_token)

        if (resp.status_code == 200):
            json_resp = resp.json()

            device_details = json_resp['data']
            
            return device_details
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to reset the "pump clean" countdown timer on Petoneer Fountain - Server Error')
