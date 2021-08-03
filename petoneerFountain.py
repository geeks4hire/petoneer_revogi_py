"""
Holds device status information for an individual Petoneer smart pet fountain
"""
from datetime import time, date, datetime
import logging
import urllib.parse
import math
import json

from petoneerErrors import *

class PetoneerFountain:

    """
    Class to interface with the cloud-based API for the Revogi Smart Home equipment
    """

    API_URL                         = "https://as.revogi.net/app"

    API_DEVICE_DETAILS_PATH         = "/pww/31101"
    API_DEVICE_SWITCH_PATH          = "/pww/21101"
    API_DEVICE_TIMER_PATH           = "/pww/21102"
    API_DEVICE_LED_PATH             = "/pww/21104"

    API_RESET_CLEAN_PUMP_TIMER      = "/pww/21103"
    API_RESET_FILTER_CHANGE_TIMER    = "/pww/21105"
    API_RESET_WATER_CHANGE_TIMER    = "/pww/21107"

    SECONDS_FOUNTAIN_WATER_CHANGE   = 5 * 24 * 60 * 60
    SECONDS_FOUNTAIN_FILTER_CHANGE  = 30 * 24 * 60 * 60
    SECONDS_FOUNTAIN_CLEAN_PUMP     = 60 * 24 * 60 * 60 
    
    Debug                           = 1 

    def __init__(self, fountain_serial_number:str, api_access_token:str, device_info_json=None):
        self._id = fountain_serial_number
        self._access_token = api_access_token
        self._device_info_json = device_info_json
        self._pump = PetoneerFountainPumpDetails(self, device_info_json)
        self._water = PetoneerFountainWaterDetails(self, device_info_json)
        self._filter = PetoneerFountainFilterDetails(self, device_info_json)
        self._led_display = PetoneerFountainLedDetails(self, device_info_json)

    def to_json(self):
        # public_fields = {
            # "device_id": self.device_id,
            # "pump": self.pump,
            # "water": self.water,
            # "filter": self.filter,
            # "led_display": self.led_display
        # }
        #return json.dumps(public_fields, indent = 4, default=lambda o: o.__dict__)
        json.dump(self)
        #return json.dumps(self, indent = 4, default=lambda o: o.__dict__)

    def __str__(self):
        return self.to_json(self)

    def _debug(self, msg):
        print(msg)
        #pass
        return

    @property
    def device_id(self):
        return self._id

    @property
    def pump(self):
        return self._pump
        # status = {
            # "is_pump_on" : self._is_pump_on,
            # "is_pump_scheduled" : self._is_pump_scheduled,
            # "pump_schedule" : {
                # "start_time" : self._pump_schedule_start_time,
                # "end_time": self._pump_schedule_end_time
            # },
            # "is_pump_cleaning_required": self._is_pump_clean_required,
            # "pump_cleaning_remaining": {
                # "days": self._pump_clean_remaining_days,
                # "percent": self._pump_clean_remaining_percent
            # },
            # "is_pump_scheduled": self._is_pump_scheduled,
            # "pump_schedule": {
                # "start_time": self._pump_schedule_start_time,
                # "end_time": self._pump_schedule_end_time
            # }
        # }
        # return status

    @property
    def water(self):
        return self._water
        # status = {
            # "level" : {
                # "value" : self._water_level_value,
                # "percent": self._water_level_percent,
                # "label": self._water_level_label
            # },
            # "quality" : {
                # "tds_value" : self._water_tds_level,
                # "label": self._water_quality_label
            # },
            # "is_water_change_required" : self._is_water_change_required,
            # "water_change_remaining": {
                # "days": self._water_change_remaining_days,
                # "percent": self._water_change_remaining_percent
            # }
        # }
        # return status

    @property
    def filter(self):
        return self._filter
        # status = {
            # "is_filter_change_required" : self._is_filter_change_required,
            # "filter_change_remaining" : {
                # "days": self._filter_change_remaining_days,
                # "percent": self._filter_change_remaining_percent
            # }
        # }
        # return status

    @property
    def led_display(self):
        return self._led_display
        # status = {
            # "is_led_on" : self._is_led_on,
            # "is_led_dimmed" : self._is_led_dimmed,
            # "is_led_dimming_scheduled": self._is_led_dimming_scheduled,
            # "led_dimming_schedule": {
                # "start": self._led_dimming_schedule_start_time,
                # "end": self._led_dimming_schedule_end_time
            # }
        # }
        # return status




    # def _is_pump_on(self):
        # return True
# 
    # def _is_pump_scheduled(self):
        # return True
# 
    # def _pump_schedule_start_time(self):
        # return time(0,0,0)
# 
    # def _pump_schedule_end_time(self):
        # return time(23,59,0)
# 
    # def _is_pump_clean_required(self):
        # return False
# 
    # def _pump_clean_remaining_days(self):
        # return 30
# 
    # def _pump_clean_remaining_percent(self):
        # return 100
# 
    # def _is_led_on(self):
        # return True
# 
    # def _is_led_dimmed(self):
        # return False
# 
    # def _is_led_dimming_scheduled(self):
        # return False
# 
    # def _led_dimming_schedule_start_time(self):
        # return time(0,0,0)
    # 
    # def _led_dimming_schedule_end_time(self):
        # return time(0,0,0)
    # 
    # def _is_filter_change_required(self):
        # return False
# 
    # def _filter_change_remaining_days(self):
        # return 30
# 
    # def _filter_change_remaining_percent(self):
        # return 100
# 
    # def _is_water_change_required(self):
        # return False
# 
    # def _water_change_remaining_days(self):
        # return 5
# 
    # def _water_change_remaining_percent(self):
        # return 100
# 
    # def _water_level_value(self):
        # return 4
# 
    # def _water_level_percent(self):
        # return 100
# 
    # def _water_level_label(self):
        # return "Full"
    # 
    # def _water_tds_level(self):
        # return 20
# 
    # def _water_quality_label(self):
        # return "Excellent"

# -------------------------------------------------

class PetoneerFountainWaterDetails:
    """
    Internal Class for PetoneerFountain object to hold properties related to 
    Water level and Quality within Petoneer Fountain 
    """

    def __init__(self, parent, device_info_json=None):
        self._parent = parent
        self._device_info_json = device_info_json
        self._water_level = {
            "value" : 4,
            "percent": 100,
            "label": "Full"
        }
        self._water_quality = {
            "tds_value" : 30,
            "label": "Excellent"
        }
        self._is_water_change_required = False
        self._water_change_remaining = {
            "days": 5,
            "percent": 100
        }

    # def to_json(self):
        # return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
# 
    # def __str__(self):
        # return self.to_json(self)

    def update(self, device_info_json):
        self._device_info_json = device_info_json

    @property
    def water_level(self):
        values = {
            "value" : 4,
            "percent": 100,
            "label": "Full"            
        }
        return values

    @property
    def water_quality(self):
        values = {
            "tds_value" : 30,
            "label": "Excellent"
        }
        return values

    @property
    def is_water_change_required(self):
        return False

    @property
    def water_change_remaining(self):
        values = {
           "days": 5,
           "percent": 100
        }
        return values
        
# -------------------------------------------------

class PetoneerFountainPumpDetails:
    """
    Internal Class for PetoneerFountain object to hold properties related to 
    Pump operation, cleaning needs, and schedule within Petoneer Fountains 
    """

    def __init__(self, parent, device_info_json=None):
        self._parent = parent
        self._device_info_json = device_info_json
        self._is_pump_on = True
        self._is_pump_scheduled = False,
        self._pump_schedule = {
            "start_time" : time(0,0,0),
            "end_time": time(0,0,0)
        }
        self._is_pump_cleaning_required = False
        self._pump_cleaning_remaining = {
            "days": 60,
            "percent": 100
        }

    # def to_json(self):
        # return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
# 
    # def __str__(self):
        # return self.to_json(self)

    def update(self, device_info_json):
        self._device_info_json = device_info_json

    @property
    def is_pump_on(self):
        return True

    @property
    def is_pump_scheduled(self):
        return False

    @property
    def pump_schedule(self):
        values = {
           "start_time": time(0,0,0),
           "end_time": time(0,0,0)
        }
        return values

    @property
    def is_pump_cleaning_required(self):
        return False

    @property
    def pump_cleaning_remaining(self):
        values = {
            "days": 60,
            "percent": 100
        }
        return values

# -------------------------------------------------

class PetoneerFountainFilterDetails:
    """
    Internal Class for PetoneerFountain object to hold properties related to 
    Filter status and cleaning needs within Petoneer Fountains 
    """

    def __init__(self, parent, device_info_json=None):
        self._parent = parent
        self._device_info_json = device_info_json
        self._is_filter_change_required = False
        self._filter_change_remaining = {
            "days": 30,
            "percent": 100
        }

    # def to_json(self):
        # return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
# 
    # def __str__(self):
        # return self.to_json(self)

    def update(self, device_info_json):
        self._device_info_json = device_info_json

    @property
    def is_filter_change_required(self):
        return False

    @property
    def filter_change_remaining(self):
        values = {
            "days": 30,
            "percent": 100
        }
        return values

# -------------------------------------------------

class PetoneerFountainLedDetails:
    """
    Internal Class for PetoneerFountain object to hold properties related to 
    LEDs Display and dimming schedule within Petoneer Fountains 
    """

    def __init__(self, parent, device_info_json=None):
        self._parent = parent
        self._device_info_json = device_info_json
        self._is_led_on = False
        self._is_led_dimmed = False
        self._is_led_dimming_scheduled = False
        self._led_dimming_schedule = {
                "start": time(0,0,0),
                "end": time(0,0,0)
        }

    # def to_json(self):
        # return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
# 
    # def __str__(self):
        # return self.to_json(self)

    def update(self, device_info_json):
        self._device_info_json = device_info_json

    @property
    def is_led_on(self):
        return True

    @property
    def is_led_dimmed(self):
        return False

    @property
    def is_led_dimming_scheduled(self):
        return False

    @property
    def led_dimming_schedule(self):
        values = {
            "start": time(0,0,0),
            "end": time(0,0,0)
        }
        return values
