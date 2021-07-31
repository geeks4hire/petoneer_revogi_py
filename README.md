# petoneer_revogi_py

__Usage:__

    pet = Petoneer();

### Authenticate with Petoneer API
    pet.auth("<<EMAIL>>", "<<PASSWORD>>")

### Obtain list of Petoneer fountains linked with user account
    devices = pet.get_registered_devices()
    pprint(devices)

### Obtain device info and status [based on device serial number]
    fountain = pet.get_device_details("<<SERIAL_NO>>")
    pprint(fountain)

### Switch on/off fountain pump [based on device serial number]
    pet.turn_off("<<SERIAL_NO>>")
    pet.turn_on("<<SERIAL_NO>>")

### Control LED's on fountain [inc dimmed or full intensity]
    pet.turn_leds_off("<<SERIAL_NO>>")
    pet.turn_leds_on("<<SERIAL_NO>>")
    pet.turn_leds_on("<<SERIAL_NO>>", leds_dimmed=True)
