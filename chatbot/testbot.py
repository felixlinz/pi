import re
import csv
import time
import datetime
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class Conditions:
    temperature : int
    humidity : int
    enddate : datetime 


def main():
    
    """
    while True:
        if (message:= processingـincomingـmessages(input("Message: "))):
            print(message)
    """
    
    adjust_targets(temperature = int(input("temp:  ")))
    adjust_targets(humidity = int(input("humid:  ")))
    adjust_targets(duration = int(input("fermenation time in hours:  ")))
    

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
                return f"current conditions placeholder"
            elif match.group(2) == "set vent":
                return f"Ventilation set to {match.group(3)} % of the Time Venting"
        except ValueError:
            return f"specified numeric value for {match.group(2)} wasn't specified correctly\nUse Numeric values without any extra Symbols"
    else: 
        attempt = re.search("^(ferment|fermentation)", text)
        if attempt:
            return "Fermentation Chamber Please type one of these commands: *ferment* + \n*set temp- ?* \n*set temp- ?*\n*set humidity- ?*\n*set duration- ?*\n*turn off*\n*conditions-*\n*set vent- ?*\n*Avoid any °C, % or other Symbols*"

def adjust_targets(temperature = None, humidity = None, duration = None):
    with open ("__targets.csv__", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            temp = row["temperature"]
            humid = row["humidity"]
            enddate = row["enddate"]
        targets = Conditions(temp, humid, enddate)
        
    if temperature:
        targets.temperature = temperature        
    elif humidity:
        targets.humidity = humidity        
    elif duration:
        targets.time = datetime.now() + timedelta(hours=duration)
        
    with open("__targets.csv__", "w") as file:
        fieldnames = ["temperature", "humidity", "enddate"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({"temperature":targets.temperature, "humidity":targets.humidity, "enddate":targets.enddate})
        
            
if __name__=="__main__":
    main()