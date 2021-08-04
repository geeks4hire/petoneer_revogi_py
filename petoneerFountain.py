"""
Holds device status information for an individual Petoneer smart pet fountain
"""
from datetime import time, date, datetime
import json

from petoneerErrors import *
from petoneerFountainDetails import *
from petoneerHelpers import *

class PetoneerFountain:

    """
    Class to interface with the cloud-based API for the Revogi Smart Home equipment
    """

    def __init__(self, fountain_serial_number:str, api_access_token:str):
        self._id = fountain_serial_number
        self._access_token = api_access_token
        self._device_info_json = None
        self._device_info_last_updated = None
        self._device_schedule_info_json = None
        self._pump = PetoneerFountainDetails_PumpDetails(self)
        self._water = PetoneerFountainDetails_WaterDetails(self)
        self._filter = PetoneerFountainDetails_FilterDetails(self)
        self._led_display = PetoneerFountainDetails_LedDetails(self)

        # Initialise property values based on provided JSON data
        self.update()

    def to_json(self):
        return json.dump(self)
        #return json.dumps(self, indent = 4, default=lambda o: o.__dict__)

    # def __str__(self):
        # return self.to_json(self)

    def _debug(self, msg):
        print(msg)
        #pass
        return

    def update(self):
        # Retrieve up-to-date info from server API if last update was more than 
        # 15 seconds ago...
        if (self._device_info_last_updated == None) or (
            (datetime.now() - self._device_info_last_updated).total_seconds() > 30):
            
            self._getDeviceDetails()

        # Update all values based on new device info JSON data
        self._pump.update(self._device_info_json, self._device_schedule_info_json)
        self._water.update(self._device_info_json)
        self._filter.update(self._device_info_json)
        self._led_display.update(self._device_info_json)
        ##
        ## TODO:  Parse JSON and update properties with new values

    def _getDeviceDetails(self):
        if (self._id == ""):
            raise PetoneerInvalidArgument('PetoneerFountain._req', 'PetoneerFountain.device_id', 'The device serial number must be provided')

        if (Debug):
            print(f"Getting details for device {self._id}")

        payload = { 
            "sn": self._id, 
            "protocol": "3" 
        }

        #
        # Request main device details from Petoneer API
        #
        resp = PetoneerHelpers.getAPIrequest(API_DEVICE_DETAILS_PATH, payload, self._access_token)

        if(resp.status_code == 200):
            json_resp = resp.json()

            if (json_resp['code'] == 200):
                self._device_info_json = json_resp['data']
            else:
                raise PetoneerInvalidServerResponse(resp.http_code, resp.url, resp.text, 'Unable to obtain Petoneer Fountain device details - Unexpected Server Response')
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to obtain Petoneer Fountain device details - Server Error')

        #
        # Second API call to obtain any configured fountain operating schedule info
        #
        resp = PetoneerHelpers.getAPIrequest(API_DEVICE_SCHEDULE_DETAILS_PATH, payload, self._access_token)

        if(resp.status_code == 200):
            json_resp = resp.json()

            if (json_resp['code'] == 200):
                self._device_schedule_info_json = json_resp['data']
            else:
                raise PetoneerInvalidServerResponse(resp.http_code, resp.url, resp.text, 'Unable to obtain Petoneer Fountain device details - Unexpected Server Response')
        else:
            raise PetoneerServerError(resp.status_code, resp.url, resp.text, 'Unable to obtain Petoneer Fountain device details - Server Error')

        self._device_info_last_updated = datetime.now()

    @property
    def device_id(self):
        return self._id

    @property
    def pump(self):
        return self._pump

    @property
    def water(self):
        return self._water

    @property
    def filter(self):
        return self._filter

    @property
    def led_display(self):
        return self._led_display

# -------------------------------------------------
