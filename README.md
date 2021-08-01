# petoneer_revogi_py

### Purpose: ###

Connects to Revogi cloud API servers to communicate with **Petoneer Fresco** range of internet-connected smart pet water fountains. 

Obtain status of fountain devices, switch on/off the pump or LEDs on the unit, and obtain information on water level and water quality/pollutants amount. 

Also retrieves information as to when actions needs to be taken (such as replacing the remaining water, installing a new active filter cartridge, or cleaning the inside of the water pump), and reset the countdown timers after these user actions have been completed.

Tested on the **Petoneer Fresco Pro** Pet Fountain.
### Usage: ###

    pet = Petoneer();

#### Authenticate with Petoneer API ####
    pet.auth("<<EMAIL>>", "<<PASSWORD>>")

Returns:
````
Authenticating to https://as.revogi.net/app as myEmail@icloud.com...
Authentication successful - token ***123d
````

#### Obtain list of Petoneer fountains linked with user account ####
    devices = pet.get_registered_devices()
    pprint(devices)

Returns:
````
Getting All Devices

[{'dataAdd': '',
  'gateway_ip': '',
  'ip': '192.168.1.33',
  'line': 1,
  'mac': 'B0:F8:00:11:22:33',
  'name': 'Laundry Fountain',
  'pname': [],
  'protect': [],
  'register': 1,
  'sak': '464646464646',
  'sn': 'PWW1000000000000',
  'socket_type': 'WebSocket',
  'userId': 91234567890123456,
  'ver': '2.60',
  'wifiRouter': 'MY-WIFI-NETWORK'}]
````

#### Obtain device info and status [based on device serial number] ####
    fountain = pet.get_device_details("<<SERIAL_NO>>")
    pprint(fountain)

Returns:
````
Getting details for device PWW1000000000000

{'changeFilter': ['30 days', '100 %'],
 'changeWater': ['5 days', '100 %'],
 'cleanPump': ['60 days', '100 %'],
 'filtertime': 1627799588,
 'led': 10,
 'ledmode': 1,
 'ledsDimmingSchedule': ['00:00:00', '00:00:00'],
 'ledsStatus': 'Off',
 'level': 3,
 'motortime': 1627799639,
 'pumpStatus': 'On',
 'section': [0, 0],
 'switch': 1,
 'tds': 28,
 'tdslevel': 0,
 'time': 1627799655,
 'waterLevel': ['75%', 'Good'],
 'waterQuality': 'Excellent',
 'watertime': 1627799510}
````

#### Switch on/off fountain pump [based on device serial number] ####
    pet.turn_off("<<SERIAL_NO>>")
    pet.turn_on("<<SERIAL_NO>>")

#### Control LED's on fountain [inc dimmed or full intensity] ####
    pet.turn_leds_off("<<SERIAL_NO>>")
    pet.turn_leds_on("<<SERIAL_NO>>")
    pet.turn_leds_on("<<SERIAL_NO>>", leds_dimmed=True)

#### Reset the countdown timer for changing water in fountain ####
    pet.reset_water_change_timer("<<SERIAL_NO>>")

*__Note:__ Petoneer recommends changing over for fresh 
    water every 5 days.*

#### Reset the countdown timer for changing filter in fountain ####
    pet.reset_filter_change_timer("<<SERIAL_NO>>")

*__Note:__ Petoneer recommends changing over for a new 
    filter every 30 days (unless alerted earlier).*

#### Reset the countdown timer for deep cleaning pump within fountain ####
    pet.reset_clean_pump_timer("<<SERIAL_NO>>")

*__Note:__ Petoneer recommends removing and thoroughly cleaning out
    the fountain's pump every 60 days.*

### Credit: ###
This library is forked from the initial [[petoneer_revogi_py](https://github.com/sh00t2kill/petoneer_revogi_py)] library, created by [sh00t2kill](https://github.com/sh00t2kill). 

Additional capabilities and error handling have been added to prepare this API integration for use within a Home Assistant smart home add-on (*COMING SOON*).