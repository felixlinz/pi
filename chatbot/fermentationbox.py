import json
import requests
from datetime import datetime, timedelta
import re
import smbus2
import bme280
import csv
import time
from dataclasses import dataclass

class Fermenter:
    def __init__(self):
        self.conditions = self.current_conditions()
        self.targets = self.target()
        self.temperature = self.conditions.temperature
        self.temptarget = self.targets.temperature
        self.humidity = self.conditions.humidity
        self.humidtarget = self.targets.humidity
        self.oxygen = self.conditions.oxygen
        self.oxytarget = self.targets.oxygen
        self.duration = self.conditions.time
        self.durtarget = self.targets.time


    def current_conditions(self):
        port = 1
        address = 0x76
        bus = smbus2.SMBus(port)

        calibration_params = bme280.load_calibration_params(bus, address)
        
        data = bme280.sample(bus, address, calibration_params)
        return Conditions(int(data.temperature), int(data.humidity), str(datetime.now()), int(data.pressure))


    def target(self):
        with open("targets.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                Targets = Conditions(row["temperature"], row["humidity"], row["datetime"], row["oxygen"])

            return Targets

    def adjust_temperature(self):
        while self.temperature < self.temptarget:
            self.heatpin = True 
            sleep(5)

class NewFermenter(Fermenter):
    def __init__(self, temperature, humidity, duration, oxygen):
        self.note_targets(temperature, humidity, duration, oxygen)

    def note_targets(self, temperature, humidity, duration, oxygen):
        with open("targets.csv", "w") as file:
            enddate = datetime.now() + timedelta(hours=duration)
            fieldnames = ["temperature", "humidity", "datetime", "oxygen"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({"temperature":int(temperature), "humidity":int(humidity), "datetime":enddate, "oxygen":int(oxygen)})

@dataclass
class Conditions:
    temperature : int
    humidity : int
    time : str 
    oxygen : int


def main():
    Box = NewFermenter(28, 55, 11, 22)
    superbox = Fermenter()
    print(superbox.conditions)


if __name__== "__main__":
    main()
