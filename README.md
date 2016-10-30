# Gardener Bear
Raspberry Pi scripts for a Bear modified to monitor plant moisture and water some pots with a Twitter-controlled interface.

## Materials needed
1. Original ELC My First Talking Ted: £9 http://www.elc.co.uk/soft-toys-and-teddy-bears/my-first-talking-ted/130651.html (£2 from charity shop)
2. Raspberry Pi Zero: Raspberry Pi Zero - Zero + Essentials Kit: £10 https://thepihut.com/products/raspberry-pi-zero?variant=14062725188
3. Raspberry Pi Camera Module V2: £21 https://thepihut.com/products/raspberry-pi-camera-module (£6.39 for noname camera from Hong Kong)
4. Raspberry Pi Zero Camera Adapter: £4 https://thepihut.com/products/raspberry-pi-zero-camera-adapter
5. USB Wifi Adapter for the Raspberry Pi: £6 https://thepihut.com/collections/all-of-the-things/products/usb-wifi-adapter-for-the-raspberry-pi (£1.34 from Hong Kong)
6. Soil Moisture Sensor Detector Hygrometer with Dual output mode, LM393 comparator chip: £1 from eBay http://www.ebay.co.uk/itm/271811882078
7.
8. 2-Channel 5V Relay 10A Module Board Opto Isolated Arduino Raspberry Pi: £2.34 from eBay http://www.ebay.co.uk/itm/182064609067
9. Dupont Female to Female 10cm Jumper Wire: £2 for 40 pieces http://www.ebay.co.uk/itm/181988213590
10. VOCHE® 10PC MICRO IRRIGATION WATERING SYSTEM AUTOMATIC PLANT POT WATER DRIP KIT: £4.15 from eBay http://www.ebay.co.uk/itm/381653890232
11. A power source for the pump and a power source for the pi zero; I used an old USB HTC phone charger with a micro-USB cable for the pi zero and an old USB cable that needed to be cut to connect to the relay. The ELC bear conveniently comes with a 3 or AA battery case that you can also use to power the relay.

## Project files
### auth.py
### gardenerbear_full.py
### gardenerbear_moisturesensor.py
### gardenerbear_startwater.py
### gardenerbear_stopwater.py
### gardenerbear_twitter.py
### gardenerbear.sh

## Attributions

Portions of this project's code are taken from the following repositories:
https://github.com/modmypi/Moisture-Sensor, ModMyPi's take on the soil moisture sensor. Includes the email functionality.
http://www.instructables.com/id/Raspberry-Pi-Irrigation-Controller/, JenFoxBot's take on the relay code for a solenoid valve.
https://github.com/jenfoxbot/SoilSensorAPI, JenFoxBot's take on the soil moisture sensor. Includes the file logging functionality idea (Apache License).
https://github.com/cilynx/raspi, Randy C. Will (@cilynx)'s take on the soil moisture sensor. Includes the polling at set intervals functionality to delay sensor corrosion (MIT License).
https://github.com/hevnsnt/tomeatyou, tomeatyou Copyright (C) 2013 hevnsnt (GNU GPL v3 License). Includes the logging function.
