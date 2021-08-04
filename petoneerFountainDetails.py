"""
Provides nested classes to provide specific info on different elements of the 
Petoneer Fountains (via the PetoneerFountain class). None of the below classes
are intended to be instantiated directly by the user - the PetoneerFountain
module will invoke and feed info to the below collection of classes.
"""
from datetime import time, date, datetime
import math
import json

from petoneerErrors import *
from petoneerHelpers import *

class PetoneerFountainDetails_WaterDetails:
    """
    Internal Class for PetoneerFountain object to hold properties related to 
    Water level and Quality within Petoneer Fountain 
    """

    def __init__(self, parent, device_info_json=None):
        self._parent = parent
        self._device_info_json = device_info_json
        self._water_level = PetoneerFountainDetails_WaterLevel(self)
        self._water_quality = PetoneerFountainDetails_WaterQuality(self)
        self._is_water_change_required = False
        self._water_change_remaining = PetoneerFountainDetails_ChangeRemaining(self)

        # Initialise property values based on provided JSON data
        if (device_info_json != None):
            self.update(device_info_json)

    def update(self, device_info_json):
        #Update all internal property values based on new device info JSON data
        self._device_info_json = device_info_json

        self._water_level.update(self._device_info_json['level'])
        self._water_quality.update(self._device_info_json['tds'])

        current_device_timestamp = self._device_info_json['time']

        self._water_change_remaining.update(
            current_device_timestamp,
            self._device_info_json['watertime'],
            SECONDS_FOUNTAIN_WATER_CHANGE)

        if (self._water_change_remaining.percent_remaining == 0):
            self._is_water_change_required = True
        else:
            self._is_water_change_required = False

    @property
    def water_level(self):
        return self._water_level

    @property
    def water_quality(self):
        return self._water_quality

    @property
    def is_water_change_required(self):
        return self._is_water_change_required

    @property
    def water_change_remaining(self):
        return self._water_change_remaining
        
# -------------------------------------------------

class PetoneerFountainDetails_PumpDetails:
    """
    Internal Class for PetoneerFountain object to hold properties related to 
    Pump operation, cleaning needs, and schedule within Petoneer Fountains 
    """

    def __init__(self, parent, device_info_json=None, device_schedule_info_json=None):
        self._parent = parent
        self._device_info_json = device_info_json
        self._device_schedule_info_json = device_schedule_info_json
        self._is_pump_on = True
        self._is_pump_scheduled = False
        self._pump_schedule = PetoneerFountainDetails_DeviceSchedule(self)
        self._is_pump_cleaning_required = False
        self._pump_cleaning_remaining = PetoneerFountainDetails_ChangeRemaining(self, 60, 100)

        # Initialise property values based on provided JSON data
        if (device_info_json != None):
            self.update(device_info_json)
 
    def update(self, device_info_json, device_schedule_info_json):
        #Update all internal property values based on new device info JSON data
        self._device_info_json = device_info_json
        self._device_schedule_info_json = device_schedule_info_json
        
        device_current_timestamp = self._device_info_json['time']
        device_current_time = PetoneerHelpers.unixTimestampToTimeObject(device_current_timestamp)

        if ('time' in self._device_schedule_info_json):    
            self._pump_schedule.update(
                    self._device_schedule_info_json['time'][0],
                    self._device_schedule_info_json['time'][1]
                )
            if(self._device_schedule_info_json['en'] == 1):
                self._is_pump_scheduled = True
            else:
                self._is_pump_scheduled = False
        else:
            self._is_pump_scheduled = False

        if (self._device_info_json['switch'] == 1):
            if (self._is_pump_scheduled):
                if (PetoneerHelpers.isCurrentTimeWithinScheduleWindow(
                    self._pump_schedule.start_time, 
                    self._pump_schedule.end_time, 
                    device_current_time
                )):
                    self._is_pump_on = True
            else:
                 self._is_pump_on = False
        else:
            self._is_pump_on = False            

        self._pump_cleaning_remaining.update(self._device_info_json['time'], self._device_info_json['motortime'], SECONDS_FOUNTAIN_CLEAN_PUMP)

        if (self._pump_cleaning_remaining.percent_remaining == 0):
            self._is_pump_cleaning_required = True
        else:
            self._is_pump_cleaning_required = False

    @property
    def is_pump_on(self):
        return self._is_pump_on

    @property
    def is_pump_scheduled(self):
        return self._is_pump_scheduled

    @property
    def pump_schedule(self):
        return self._pump_schedule

    @property
    def is_pump_cleaning_required(self):
        return self._is_pump_cleaning_required

    @property
    def pump_cleaning_remaining(self):
        return self._pump_cleaning_remaining

# -------------------------------------------------

class PetoneerFountainDetails_FilterDetails:
    """
    Internal Class for PetoneerFountain object to hold properties related to 
    Filter status and cleaning needs within Petoneer Fountains 
    """

    def __init__(self, parent, device_info_json=None):
        self._parent = parent
        self._device_info_json = device_info_json
        self._is_filter_change_required = False
        self._filter_change_remaining = PetoneerFountainDetails_ChangeRemaining(self)

        # Initialise property values based on provided JSON data
        if (device_info_json != None):
            self.update(device_info_json)

    def update(self, device_info_json):
        #Update all internal property values based on new device info JSON data
        self._device_info_json = device_info_json

        device_current_timestamp = self._device_info_json['time']
        self._filter_change_remaining.update(device_current_timestamp, self._device_info_json['filtertime'], SECONDS_FOUNTAIN_FILTER_CHANGE)

        if(self._filter_change_remaining.percent_remaining == 0):
            self._is_filter_change_required = True
        else:
            self._is_filter_change_required = False

    @property
    def is_filter_change_required(self):
        return self._is_filter_change_required

    @property
    def filter_change_remaining(self):
        return self._filter_change_remaining

# -------------------------------------------------

class PetoneerFountainDetails_LedDetails:
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
        self._led_dimming_schedule = PetoneerFountainDetails_DeviceSchedule(self)

        # Initialise property values based on provided JSON data
        if (device_info_json != None):
            self.update(device_info_json)

    def update(self, device_info_json):
        #Update all internal property values based on new device info JSON data
        self._device_info_json = device_info_json

        led_value = self._device_info_json['led']
        ledmode_value = self._device_info_json['ledmode']
        device_current_timestamp = self._device_info_json['time']
        device_current_time = PetoneerHelpers.scheduleStringToTimeObject(device_current_timestamp)

        if ('section' in self._device_info_json):
            self._led_dimming_schedule.update(self._device_info_json['section'][0], self._device_info_json['section'][1])
            self._is_led_dimming_scheduled = True

            if(PetoneerHelpers.isCurrentTimeWithinScheduleWindow(self._led_dimming_schedule.start_time,
                self._led_dimming_schedule.end_time, device_current_time)):            

                    self._is_led_dimmed = True
            else:
                self._is_led_dimmed = False
        else:
            self._led_dimming_schedule.update("0","0")
            self.is_led_dimmed = False
            self.is_led_dimming_scheduled = False

        if ((led_value == 1) or (ledmode_value == 10)):
            self._is_led_on = True
        else:
            self._is_led_on = False

    @property
    def is_led_on(self):
        return self._is_led_on

    @property
    def is_led_dimmed(self):
        return self._is_led_dimmed

    @property
    def is_led_dimming_scheduled(self):
        return self._is_led_dimming_scheduled

    @property
    def led_dimming_schedule(self):
        return self._led_dimming_schedule

# -------------------------------------------------
class PetoneerFountainDetails_ChangeRemaining:
    """
    Internal Class for PetoneerFountain object to provide "time remaining" for
    a number of maintenance parameters for the Petoneer Fountain (eg: changing
    over water, changing filters, and deep cleaning the pump). 
    """
    def __init__(self, parent, device_current_time_unix_timestamp:int = None, device_feature_unix_timestamp:int = None, threshold_interval_secs:int = 0):
        self._parent = parent
        self._device_current_time_timestamp = device_current_time_unix_timestamp
        self._device_feature_last_changed_timestamp = device_feature_unix_timestamp
        self._days_remaining_threshold_seconds = threshold_interval_secs
        if ((device_current_time_unix_timestamp != None) and (device_current_time_unix_timestamp > 0) and 
            (device_feature_unix_timestamp != None) and (device_feature_unix_timestamp > 0) and
            (threshold_interval_secs > 0)):

            self._days_remaining = self._getNumOfDaysRemaining(device_current_time_unix_timestamp, device_feature_unix_timestamp, threshold_interval_secs)
            self._percent_remaining = self._getPercentageRemaining(device_current_time_unix_timestamp, device_feature_unix_timestamp, threshold_interval_secs)
        else:
            self._days_remaining = 0
            self._percent_remaining = 0    
    
    def update(self, device_current_time_unix_timestamp: int, device_feature_unix_timestamp: int, threshold_interval_secs:int):
        if ((device_current_time_unix_timestamp > 0) and (device_feature_unix_timestamp > 0) and (threshold_interval_secs > 0)):
            self._days_remaining = self._getNumOfDaysRemaining(device_current_time_unix_timestamp, device_feature_unix_timestamp, threshold_interval_secs)
            self._percent_remaining = self._getPercentageRemaining(device_current_time_unix_timestamp, device_feature_unix_timestamp, threshold_interval_secs)
        else:
            self._days_remaining = 0
            self._percent_remaining = 0

    @property
    def days_remaining(self):
        return self._days_remaining

    @property
    def percent_remaining(self):
        return self._percent_remaining

    def _getNumOfDaysRemaining(self, device_current_time_unix_timestamp:int, device_feature_unix_timestamp:int, threshold_interval_secs:int):
        date1 = datetime.fromtimestamp(device_feature_unix_timestamp)
        date2 = datetime.fromtimestamp(device_current_time_unix_timestamp)

        seconds_difference = (date2 - date1).total_seconds()
        days_remaining = math.ceil((threshold_interval_secs - seconds_difference)/60/60/24)

        return days_remaining

    def _getPercentageRemaining(self, device_current_time_unix_timestamp: int, device_feature_unix_timestamp: int, threshold_interval_secs):
        date1 = datetime.fromtimestamp(device_feature_unix_timestamp)
        date2 = datetime.fromtimestamp(device_current_time_unix_timestamp)

        seconds_difference = (date2 - date1).total_seconds()
        percent_remaining = round(((threshold_interval_secs - seconds_difference) / threshold_interval_secs) * 100)

        return percent_remaining

# -------------------------------------------------

class PetoneerFountainDetails_DeviceSchedule:
    """
    Internal Class for PetoneerFountain object to provide a pair of times (start + end) 
    in native Python datetime.time objects for the two schedules that are configurable
    within the Petoneer Pet Fountain - LED dimming times (eg: night mode), and pump
    schedule (if you want to turn the fountain off completely overnight). 
    """

    def __init__(self, parent, start_schedule_time_str:str = "", end_schedule_time_str:str = ""):
        self._parent = parent
        if (start_schedule_time_str == ""):
            self._start_time = time(0,0,0)
        else:
            self._start_time = PetoneerHelpers.scheduleStringToTimeObject(start_schedule_time_str)
        if (end_schedule_time_str == ""):
            self._end_time = time(0,0,0)
        else:
            self._end_time = PetoneerHelpers.scheduleStringToTimeObject(end_schedule_time_str)
    
    def update(self, start_schedule_time_str:str, end_schedule_time_str:str):
        self._start_time = PetoneerHelpers.scheduleStringToTimeObject(start_schedule_time_str)
        self._end_time = PetoneerHelpers.scheduleStringToTimeObject(end_schedule_time_str)

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

# -------------------------------------------------

class PetoneerFountainDetails_WaterLevel:
    """
    Internal Class for PetoneerFountain object to hold properties related to 
    Water level
    """

    def __init__(self, parent, water_level_value=0):
        self._parent = parent
        self._water_level_value = water_level_value
        self._water_level_percent = self._getWaterLevelPercentage(water_level_value)
        self._water_level_label = self._getWaterLevelLabel(water_level_value)
    
    def update(self, water_level_value):
        self._water_level_value = water_level_value
        self._water_level_percent = self._getWaterLevelPercentage(water_level_value)
        self._water_level_label = self._getWaterLevelLabel(water_level_value)

    @property
    def value(self):
        return self._water_level_value

    @property
    def percent(self):
        return self._water_level_percent

    @property
    def label(self):
        return self._water_level_label

    def _getWaterLevelLabel(self, level_int):
        level_labels={
            0: "Empty",
            1: "Low",
            2: "Adequate",
            3: "Good",
            4: "Full"
        }
        return (level_labels.get(level_int, 'Invalid Water Level Value!'))

    def _getWaterLevelPercentage(self, level_int):
        percent_labels={
            0: "0%",
            1: "25%",
            2: "50%",
            3: "75%",
            4: "100%"
        }
        return (percent_labels.get(level_int, 'Invalid Water Level Value!'))

# -------------------------------------------------

class PetoneerFountainDetails_WaterQuality:
    """
    Internal Class for PetoneerFountain object to hold properties related to 
    Water quality (based on the Total Dissolved Solids [TDS] value returned from
    the fountain)
    """
    def __init__(self, parent, tds_value=0):
        self._parent = parent
        self._tds_value = tds_value
        self._water_quality_label = self._getWaterQualityLabel(tds_value)
    
    def update(self, tds_value):
        self._tds_value = tds_value
        self._water_quality_label = self._getWaterQualityLabel(tds_value)

    @property
    def tds_value(self):
        return self._tds_value

    @property
    def quality_label(self):
        return self._water_quality_label

    def _getWaterQualityLabel(self, tds_level_int):
        if (tds_level_int < 1):
            return "Invalid TDS Level Provided!"
        elif (tds_level_int <= 50):
            return "Excellent"
        elif (tds_level_int <= 100):
            return "Drinkable"
        # otherwise ...
        return "Undrinkable"
