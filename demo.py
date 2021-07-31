import requests
import json
import time

from pprint import pprint
from datetime import datetime as dt

from petoneer import *
#from petoneerErrors import *

from demo_settings import API_USERNAME, API_PASSWORD

petoneer_api = Petoneer()

auth_result = petoneer_api.auth(API_USERNAME, API_PASSWORD)

petoneer_devices = petoneer_api.get_registered_devices()

pprint(petoneer_devices)
print("\n ....... \n")

for fountain in petoneer_devices:
    print('Fountain ID#' + fountain['sn'])

    fountain_status = petoneer_api.get_device_details(fountain["sn"])
    pprint(fountain_status)

    print()

# Menu to demonstrate module features (against first Fountain registered with user account)
menu_input = ''
while (menu_input != "q") and (menu_input != "Q"):

    print("\n==========================================\n")
    print(" (1) - Turn OFF Fountain #0")
    print(" (2) - Turn ON Fountain #0")
    print(" (3) - Turn OFF LED's for Fountain #0")
    print(" (4) - Turn ON LEDs [Dimmed] Fountain #0")
    print(" (5) - Turn ON LEDs [Full] Fountain #0")
    print()
    print(" (Q) - Quit the demonstration")
    menu_input = input("   -> Select Option [1-5/Q]: ")

    fountain_sn = petoneer_devices[0]['sn']
    if menu_input == "1":
        print("      *** TURNING OFF FOUNTAIN...")
        petoneer_api.turn_off(fountain_sn)

    elif menu_input == "2":
        print("      *** TURNING ON FOUNTAIN...")
        petoneer_api.turn_on(fountain_sn)

    elif menu_input == "3":
        print("      *** TURNING OFF LED's...")
        petoneer_api.turn_led_off(fountain_sn)

    elif menu_input == "4":
        print("      *** TURNING ON LED's (Dimmed)...")
        petoneer_api.turn_led_on(fountain_sn, leds_dimmed=True)

    elif menu_input == "5":
        print("      *** TURNING ON LED's (Full Intensity)...")
        petoneer_api.turn_led_on(fountain_sn)

    elif (menu_input != 'q') or (menu_input != 'Q'):
        break

    else:
        print("      <-- ERROR: Invalid menu selection!")

    print("\n ....... \n")

    fountain_status = petoneer_api.get_device_details(fountain_sn)
    pprint(fountain_status)

    print()

