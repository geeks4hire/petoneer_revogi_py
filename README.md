# petoneer_revogi_py

__Usage:__

    pet = Petoneer();

### Authenticate with Petoneer API
    pet.auth("<<EMAIL>>", "<<PASSWORD>>")

### Get device info and status for fountain (based on serial number)
    fountain = pet.get_device_details("<<SERIAL_NO>>")
    pprint(fountain)

### Retrieve all registered Petoneer fountain devices linked with user account
    devices = pet.get_registered_devices() 
    pprint(devices)

### Switch on/off water pump (based on fountain serial number)
    pet.turn_off("<<SERIAL_NO>>")
    pet.turn_on("<<SERIAL_NO>>")

### Control LED's on fountain [inc dimmed or full intensity]
    pet.turn_leds_off("<<SERIAL_NO>>")
    pet.turn_leds_on("<<SERIAL_NO>>")
    pet.turn_leds_on("<<SERIAL_NO>>", leds_dimmed=True)
