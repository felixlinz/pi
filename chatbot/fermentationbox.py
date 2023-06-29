import json
import requests
from datetime import datetime, timedelta
import re
import smbus2
import bme280
import csv
import time
import RPi.GPIO as GPIO
from dataclasses import dataclass

class Fermenter:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.heatpin = 11
        self.fanpin = 7
        self.humiditypin = 13
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
    
    def core_conditions(self):
        port = 2
        address = 0x77
        bus = smbus2.SMBus(port)
        
        calibration_params = bme280.load_calibration_params(bus, address)
        data = bme280.sample(bus, address, calibration_params)
        
        return Conditions(int(data.temperature), int(data.humidity), str(datetime.now()), int(data.pressure))
        
        


    def target(self):
        with open("targets.csv", "r") as file:
            row = {"temperature": 0, "humidity": 1, "datetime": 3}
            reader = csv.DictReader(file)
            for row in reader:
                Targets = Conditions(row["temperature"], row["humidity"], row["datetime"], row["oxygen"])

            return Targets

    def adjust_temperature(self):
        while self.temperature < self.temptarget:
            GPIO.output(self.heatpin, GPIO.HIGH)
            GPIO.output(self.fanpin, GPIO.HIGH)
            time.sleep(5)
            self.temperature = self.current_conditions().temperature
        GPIO.output(self.heatpin, GPIO.LOW)
        GPIO.output(self.fanpin, GPIO.LOW)
        
    def adjust_humidity(self):
        while self.temperature < self.temptarget:
            GPIO.output(self.heatpin, GPIO.HIGH)
            GPIO.output(self.fanpin, GPIO.HIGH)
            time.sleep(5)
            self.humidity = self.current_conditions().humidity
        GPIO.output(self.heatpin, GPIO.LOW)
        GPIO.output(self.fanpin, GPIO.LOW)


class NewFermenter():
    def __init__(self, temperature, humidity, duration, oxygen):
        self.note_targets(temperature, humidity, duration, oxygen)

    def note_targets(self, temperature, humidity, duration, oxygen):
        with open("targets.csv", "w") as file:
            enddate = datetime.now() + timedelta(hours=duration)
            fieldnames = ["temperature", "humidity", "datetime", "oxygen"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({"temperature":int(temperature), "humidity":int(humidity), "datetime":enddate, "oxygen":int(oxygen)})
        
        return "targets.csv"

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
