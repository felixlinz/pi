import requests
from datetime import datetime, timedelta
import csv
import time
from dataclasses import dataclass

class Fermenter:
    def __init__(self):
        self.targetfile()
        self.heatpin = 11
        self.fanpin = 7
        self.humiditypin = 13
        self.conditions = self.current_conditions()
        self.temperature = self.conditions.temperature
        self.temptarget = self.targets.temperature
        self.humidity = self.conditions.humidity
        self.humidtarget = self.targets.humidity
        self.oxygen = self.conditions.oxygen
        self.oxytarget = self.targets.oxygen
        self.duration = self.conditions.time
        self.durtarget = self.targets.time

    def targetfile(self):
        with open("__targets__.csv", "w") as file:
            fieldnames = ["temperature", "humidity", "enddate"]
            writer = csv.DictWriter(file, fieldnames = fieldnames)
            writer.writeheader()
            writer.writerow(
                {"temperature":28, "humidity":85, "enddate": datetime.now()  + timedelta(hours=48)}
            )
    
        
    def target(self):
        with open("__targets__.csv", "r") as file:
            row = {"temperature": 0, "humidity": 1, "datetime": 3}
            reader = csv.DictReader(file)
            for row in reader:
                Targets = Conditions(row["temperature"], row["humidity"], row["datetime"], row["oxygen"])
                
            return Targets
        
    
    def check_finished(self):
        if datetime.now() > self.targets.time:
            return True
        
        return False
        
        
    def adjust_targets(self, temperature = None, humidity = None, duration = None):
        with open ("__targets__.csv", "r") as file:
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
            
        with open("__targets__.csv", "w") as file:
            fieldnames = ["temperature", "humidity", "enddate"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({"temperature":targets.temperature, "humidity":targets.humidity, "enddate":targets.enddate})
        
        self.targets = targets
            





@dataclass
class Conditions:
    temperature : int
    humidity : int
    enddate : datetime 

class Chatbox:
    def __init__(self):
        


if __name__== "__main__":
    main()
