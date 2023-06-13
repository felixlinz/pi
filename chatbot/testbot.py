import re
import smbus2
import bme280
import csv
import time
import plotext as plt 
import datetime

def main():
    while True:
        if (message:= processingـincomingـmessages(input("Message: "))):
            print(message)
    

def processingـincomingـmessages(text):
    match = re.search(r"^(ferment)\b.*\b(set \w*|conditions)\b.*\-\s*(\d*)", text)
    if match:
        try:
            if match.group(2) == "set temp":
                return f"temperature set to {int(match.group(3))} Degrees"
            elif match.group(2) == "set humidity":
                return f"humidity set to {int(match.group(3))} Percent Air Wetness"
            elif match.group(2) == "set duration":
                return f"duration set to {int(match.group(3))} Hours"
            elif match.group(2) == "conditions":
                return current_conditions()
            elif match.group(2) == "set vent":
                return f"Ventilation set to {match.group(3)} % of the Time Venting"
        except ValueError:
            return f"specified numeric value for {match.group(2)} wasn't specified correctly\nUse Numeric values without any extra Symbols"
    else: 
        attempt = re.search("^(ferment|fermentation)", text)
        if attempt:
            return "Fermentation Chamber Please type one of these commands: *ferment* + \n*set temp- ?* \n*set temp- ?*\n*set humidity- ?*\n*set duration- ?*\n*turn off*\n*conditions-*\n*set vent- ?*\n*Avoid any °C, % or other Symbols*"

        
        
    
    
    
def current_conditions():
    port = 1
    address = 0x76
    bus = smbus2.SMBus(port)

    calibration_params = bme280.load_calibration_params(bus, address)

    data = bme280.sample(bus, address, calibration_params)
    
    return f"""Current Climate Conditions, Fermentation Chamber
    {int(data.temperature)} °C Temperature
    {int(data.humidity)} % Humidity
    {int(data.pressure)} PSI Ambient Pressure """
        
            
if __name__=="__main__":
    main()