import requests
from datetime import datetime, timedelta
import smbus2
import json
import bme280
import csv
import time
import RPi.GPIO as GPIO
import re
from dataclasses import dataclass
from threading import Thread
import atexit

class Fermenter:
    def __init__(self, heaptin = 11, fanpin = 7, humiditypin = 13):
        GPIO.setmode(GPIO.BCM)
        self._on = False
        self.targets = self.target()
        self.heatpin = heaptin
        self.fanpin = fanpin
        self.humiditypin = humiditypin
        self._exceptions = []
        atexit.register(self.cleanup)
        
    def problemreport(self):
        if self._exceptions:
            response = f"The following problems occured {[exception for exception in self._exceptions]}"
            self._exceptions = []
            return response
        return False
        
    def turn_on(self):
        self._on = True
        self.heatcontrol = Thread(target=self.reach_temperature)
        self.humiditycontrol = Thread(target=self.reach_humidity)
        self.heatcontrol.start()
        self.humiditycontrol.start()
        
    def turn_off(self):
        self.adjust_targets(temperature=0, humidity=0, duration=0)
        self._on = False

    def default_program(self):
        with open("__targets__.csv", "w") as file:
            fieldnames = ["temperature", "humidity", "enddate"]
            writer = csv.DictWriter(file, fieldnames = fieldnames)
            writer.writeheader()
            writer.writerow(
                {"temperature":28, "humidity":85, "enddate": datetime.now()  + timedelta(hours=48)}
            )
            
    def current_conditions(self):
        port = 1
        address = 0x76
        bus = smbus2.SMBus(port)

        calibration_params = bme280.load_calibration_params(bus, address)
        data = bme280.sample(bus, address, calibration_params)
        
        return Conditions(int(data.temperature), int(data.humidity), datetime.now(), int(data.pressure))
    
    
    def target(self):
        try:
            with open("__targets__.csv", "r") as file:
                row = {"temperature": 0, "humidity": 1, "datetime": 3}
                reader = csv.DictReader(file)
                for row in reader:
                    Targets = Conditions(row["temperature"], row["humidity"], row["datetime"], row["oxygen"])
                return Targets
            
        except FileNotFoundError as e:
            self._exceptions.append(e)
            self.default_program()
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
        if self._on != True:
            self._on = True
        with open ("__targets__.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                temp = row["temperature"]
                humid = row["humidity"]
                enddate = row["enddate"]
            targets = Conditions(temp, humid, enddate)
            
        if temperature:
            targets.temperature = temperature        
        if humidity:
            targets.humidity = humidity        
        if duration:
            targets.time = datetime.now() + timedelta(hours=duration)
            
        with open("__targets__.csv", "w") as file:
            fieldnames = ["temperature", "humidity", "enddate"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({"temperature":targets.temperature, "humidity":targets.humidity, "enddate":targets.enddate})
        
        self.targets = targets
            

    def reach_temperature(self):
        temperature = self.current_conditions().temperature
        temptarget = self.target().temperature
        try:
            while self._on == True:
                self.reach_value(temperature,temptarget,self.heatpin,"temperature")
        except Exception as e:
            self._exceptions.append(e)
            self.turn_off()
            print(f"An error occurred in reach_temperature: {e}")
        
    def reach_humidity(self):
        humidity = self.current_conditions().humidity
        humidtarget = self.target().humidity
        try:
            while self._on == True:
                self.reach_value(humidity, humidtarget, self.humiditypin, "humidity")
        except Exception as e:
            self._exceptions.append(e)
            self.turn_off()
            print(f"An error occurred in reach_humidity: {e}")
            
    def reach_value(self, state, target, controlpin, parameter):
        if state < target:
            if parameter == "temperature":
                GPIO.output(self.fanpin, GPIO.HIGH)
            GPIO.output(controlpin, GPIO.HIGH)
            time.sleep(5)
            
            if parameter == "temperature":
                state = self.current_conditions().temperature
                target = self.targets.temperature
            elif parameter == "humidity":
                state = self.current_conditions().humidity
                target = self.targets.humidity
            return True
                
            
        elif state > target:
            if parameter == "temperature":
                GPIO.output(self.fanpin, GPIO.LOW)
            GPIO.output(controlpin, GPIO.LOW)
            time.sleep(5)
            
            if parameter == "temperature":
                state = self.current_conditions().temperature
                target = self.targets.temperature
            elif parameter == "humidity":
                state = self.current_conditions().humidity
                target = self.targets.humidity
            return False
            
    def cleanup(self):
        GPIO.cleanup()



@dataclass
class Conditions:
    temperature : int
    humidity : int
    enddate : datetime 

class ChatBox():    
    def __init__(self, json, fermenter, connection_url, token):
        self.fermenter = fermenter
        self.json = json
        self.dict_messages = json['data']
        self.ultraAPIUrl = str(connection_url)
        self.token = str(token)

   
    def send_requests(self, type, data):
        url = f"{self.ultraAPIUrl}{type}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        return answer.json()
    

    def send_message(self, chatID, text):
        if chatID == "unknown":
            chatID = self.dict_messages["from"]
        data = {"to" : chatID,
                "body" : text}  
        answer = self.send_requests('messages/chat', data)
        return answer
    
    
    def processingـincomingـmessages(self):
        message = self.dict_messages
        text = message["body"].lower()
        chatID = message["from"]
        match = re.search(r"^(ferment)\b.*\b(set \w*|conditions|turn off|turn on|targets)\b.*\-\s*(\d*)", text)
        if match:
            try:
                
                if match.group(2) == "set temp":
                    temptarget = int(match.group(3))
                    self.fermenter.adjust_targets(temperature = temptarget)
                    return self.send_message(chatID, f"temperature set to {temptarget} Degrees")
                
                elif match.group(2) == "set humidity":
                    humidtarget = int(match.group(3))
                    self.fermenter.adjust_targets(humidity= humidtarget)
                    return self.send_message(chatID, f"humidity set to {humidtarget} Percent Air Wetness")
                
                elif match.group(2) == "set duration":
                    durtarget = int(match.group(3))
                    self.fermenter.adjust_targets(temperature = durtarget)
                    return self.send_message(chatID, f"duration set to {durtarget} Hours")
                
                elif match.group(2) == "conditions":
                    conditions = self.fermenter.current_conditions()
                    targets = self.fermenter.target()
                    return self.send_message(chatID, conditions), f"{targets.enddate - conditions.enddate} time left over"
                
                elif match.group(2) == "targets":
                    targets = self.fermenter.target()
                    return self.send_message(chatID, targets)
                
                elif match.group(2) == "set vent":
                    return self.send_message(chatID, f"Ventilation set to {match.group(3)} % of the Time Venting")
                
                elif match.group(2) == "turn off":
                    self.fermenter.turn_off()
                    return self.send_message(chatID, f"Fermentation Chamber turned off, all bacteria dead")
                
                elif match.group(2) == "turn on":
                    self.fermenter.turn_on()
                    return self.send_message(chatID, f"Fermentation Chamber turned off, all bacteria dead")
                
            except ValueError:
                return self.send_message(chatID, f"specified numeric value for {match.group(2)} wasn't specified correctly\nUse Numeric values without any extra Symbols")
        elif (attempt := re.search(r"^(ferment|fermentation)", text)):
            return self.send_message(chatID,"Fermentation Chamber Please type one of these commands: *ferment* + \n*set temp- ?* \n*set temp- ?*\n*set humidity- ?*\n*set duration- ?*\n*turn off-*\n*conditions-*\n*set vent- ?*\n*Avoid any °C, % or other Symbols*\nfor example to set the temperature to 25 Degrees, the command woould be *ferment set temp- 25*")
        elif re.search(r"^sesam öffne dich", text):
            return self.send_message(chatID, "Schlüssel auf Strasse geworfen")


if __name__== "__main__":
    main()
