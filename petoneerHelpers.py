from datetime import time, date, datetime
import logging
import urllib.parse
import math
import json
import requests

from petoneerErrors import *
from petoneerConst import *

class PetoneerHelpers:
    """
    Class that provides static helper functions, that need to be called across multiple classes
    or scope isolated sections of this project
    """

    API_URL                             = "https://as.revogi.net/app"

    @staticmethod
    def timeObjectToScheduleString(schedule_time: datetime):
        schedule_value = (schedule_time.hour * 60) + schedule_time.min
        return schedule_value

    @staticmethod
    def scheduleStringToTimeObject(schedule_time_str):
        if (schedule_time_str == 0):
            return time(0,0,0)

        hours = math.floor(int(schedule_time_str) / 60)
        mins =  int(schedule_time_str - (hours * 60))

        if (hours <= 23) and (hours >= 0) and (mins <=59) and (mins >= 0):
            return time(hours, mins, 0)
        else:
            return time(0,0,0)

    @staticmethod
    def unixTimestampToTimeObject(unix_timestamp:str):
        return datetime.fromtimestamp(unix_timestamp).time()

    @staticmethod
    def TimeObjectToUnixTimestamp(time_obj:time):

        time_today = datetime.combine(datetime.now(), test_time) 
        unixtimestamp = int(time_today.timestamp())

        return unixtimestamp
    
    @staticmethod
    def isCurrentTimeWithinScheduleWindow(schedule_start_time:time, schedule_end_time:time, current_time:time = datetime.now().time):
        return ((schedule_start_time <= current_time) and 
            (schedule_end_time > current_time))

    @staticmethod
    def getAPIrequest(methodPath:str, payload:str, access_token=None):
        if (access_token != None) and (access_token != ""):
            headers = { 
                "accessToken": access_token
            }
        else:
            headers = {}

        # Make the request
        try:
            resp = requests.post(PetoneerHelpers.getApiUrlFromPath(methodPath), json=payload, headers=headers)
            return resp

        except Exception as e:
            raise PetoneerApiServerOffline(PetoneerHelpers.getApiUrlFromPath(methodPath), 501, 'Unable to connect to Petoneer API server - Connection Failed')

    @staticmethod
    def getApiUrlFromPath(apiPath):
        return API_URL + apiPath
