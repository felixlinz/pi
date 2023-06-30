import json
import requests
import datetime
import re
import smbus2
import bme280
import csv
import time
from fermentationbox import Fermenter



class ultraChatBot():    
    def __init__(self, json):
        self.json = json
        self.dict_messages = json['data']
        self.ultraAPIUrl = 'https://api.ultramsg.com/instance49996/'
        self.token = 'vyijsik2q818dbyp'

   
    def send_requests(self, type, data):
        url = f"{self.ultraAPIUrl}{type}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        return answer.json()

    def send_message(self, chatID, text):
        data = {"to" : chatID,
                "body" : text}  
        answer = self.send_requests('messages/chat', data)
        return answer
    
    def current_conditions(self):
        port = 1
        address = 0x76
        bus = smbus2.SMBus(port)

        calibration_params = bme280.load_calibration_params(bus, address)

        data = bme280.sample(bus, address, calibration_params)
        
        return f""" Current Climate Conditions, Dierksstrasse 17
        {int(data.temperature)} °C Temperature
        {int(data.humidity)} % Humidity
        {int(data.pressure)} psi Ambient Pressure """

    def processingـincomingـmessages(self):
        message = self.dict_messages
        text = message["body"].lower()
        chatID = message["from"]
        match = re.search(r"^(ferment)\b.*\b(set \w*|conditions|turn off)\b.*\-\s*(\d*)", text)
        if match:
            time.sleep(2)
            try:
                if match.group(2) == "set temp":
                    return self.send_message(chatID, f"temperature set to {int(match.group(3))} Degrees")
                elif match.group(2) == "set humidity":
                    return self.send_message(chatID, f"humidity set to {int(match.group(3))} Percent Air Wetness")
                elif match.group(2) == "set duration":
                    return self.send_message(chatID, f"duration set to {int(match.group(3))} Hours")
                elif match.group(2) == "conditions":
                    conditions = self.current_conditions()
                    return self.send_message(chatID, conditions)
                elif match.group(2) == "set vent":
                    return self.send_message(chatID, f"Ventilation set to {match.group(3)} % of the Time Venting")
                elif match.group(2) == "turn off":
                    return self.send_message(chatID, f"Fermentation Chamber turned off, all bacteria dead")
            except ValueError:
                return self.send_message(chatID, f"specified numeric value for {match.group(2)} wasn't specified correctly\nUse Numeric values without any extra Symbols")
        elif (attempt := re.search(r"^(ferment|fermentation)", text)):
            return self.send_message(chatID,"Fermentation Chamber Please type one of these commands: *ferment* + \n*set temp- ?* \n*set temp- ?*\n*set humidity- ?*\n*set duration- ?*\n*turn off-*\n*conditions-*\n*set vent- ?*\n*Avoid any °C, % or other Symbols*\nfor example to set the temperature to 25 Degrees, the command woould be *ferment set temp- 25*")
        elif re.search(r"^sesam öffne dich", text):
            return self.send_message(chatID, "Schlüssel auf Strasse geworfen")
        
            
        