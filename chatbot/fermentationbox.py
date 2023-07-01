import requests
from datetime import datetime, timedelta
import pygal
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
    """
    representation of the Fermentain box 
    """
    def __init__(self, heaptin = 11, fanpin = 7, humiditypin = 13):
        self.default_program()
        self._exceptions = []
        self.logfile = self.empty_logfile()
        GPIO.setmode(GPIO.BCM)
        self._on = False
        self.heatpin = heaptin
        self.fanpin = fanpin
        self.humiditypin = humiditypin
        atexit.register(self.cleanup)
        
    
    def problemreport(self):
        """
        returns a list of all problems that occured during runtime
        """
        if self._exceptions:
            response = f"The following problems occured {[exception for exception in self._exceptions]}"
            # reset after reading them out
            self._exceptions = []
            return response
        return False
        
    def turn_on(self):
        """
        starts multiple threads that constantly monitor and adjust 
        temperature and humidity
        """
        self._on = True
        self.heatcontrol = Thread(target=self.reach_temperature)
        self.humiditycontrol = Thread(target=self.reach_humidity)
        self.heatcontrol.start()
        self.humiditycontrol.start()
        
    def turn_off(self):
        """
        stops all processes
        """
        self.adjust_targets(temperature=0, humidity=0)
        self._on = False

    def default_program(self):
        """
        sets up a default program if no specific values where added 
        """
        with open("__targets__.csv", "w") as file:
            fieldnames = ["temperature", "humidity", "enddate"]
            writer = csv.DictWriter(file, fieldnames = fieldnames)
            writer.writeheader()
            writer.writerow(
                {"temperature":28, "humidity":85, "enddate": datetime.now()  + timedelta(hours=48)}
            )
            
    def current_conditions(self):
        """
        returns a Dataclass Object containing the current conditions 
        in the fermentation chamber
        """
        port = 1
        address = 0x76
        bus = smbus2.SMBus(port)

        calibration_params = bme280.load_calibration_params(bus, address)
        data = bme280.sample(bus, address, calibration_params)
        
        with open(self.logfile,"a") as file:
            fieldnames = ["temperature", "humidity", "sampledate"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerow({"temperature":data.temperature, "humidity":data.humidity, "sampledate":datetime.now()})
        
        return Conditions(int(data.temperature), int(data.humidity), datetime.now())
    
    
    def empty_logfile(self):
        with open("__conditionslog.csv","w") as file:
            fieldnames = ["temperature", "humidity", "sampledate"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
        return "__conditionslog.csv"
            
            
    def target(self):
        """
        reads out the desired values for the conditions inside the box
        """
        try:
            with open("__targets__.csv", "r") as file:
                row = {"temperature": 0, "humidity": 1, "datetime": 3}
                reader = csv.DictReader(file)
                for row in reader:
                    target = Conditions(int(row["temperature"]), int(row["humidity"]), datetime.strptime(row["enddate"], "%Y-%m-%d %H:%M:%S.%f"))
                return target
            
        except FileNotFoundError as e:
            """
            in case there is nothing setup, a default programm gets loaded
            """
            self._exceptions.append(e)
            self.default_program()
            with open("__targets__.csv", "r") as file:
                row = {"temperature": 0, "humidity": 1, "datetime": 3}
                reader = csv.DictReader(file)
                for row in reader:
                    target = Conditions(int(row["temperature"]), int(row["humidity"]), datetime.strptime(row["enddate"], "%Y-%m-%d %H:%M:%S.%f"))
                return target
            
    
    def check_finished(self):
        """
        checks if the fermentation process is done
        """
        if datetime.now() > self.targets.time:
            return True
        return False
        
        
    def adjust_targets(self, temperature = None, humidity = None, duration = None):
        """
        manipulates the targets saved in tatgets csv file
        """
        # make sure the box is on 
        self._on = True
        with open ("__targets__.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                temp = row["temperature"]
                humid = row["humidity"]
                enddate = row["enddate"]
            targets = Conditions(int(temp), int(humid), datetime.strptime(enddate,"%Y-%m-%d %H:%M:%S.%f"))
            
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
        # resetting targets
        self.targets = targets
            

    def reach_temperature(self):
        """
        loops over the target and current conditions and turns on 
        the heat while its too cold
        """
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
        """
        loops over tharget and current conditions and turns on the heat if its too cold
        """
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
        """
        used by reach heat and reach humidity to reach conditions
        """
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
        
    def datalog(self):
        """
        returns location of a jpeg with plots of the eveolvement of the conditions
        """
        temperatures = []
        humidities = []
        dates = []

        # Open your CSV file
        with open('yourfile.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Convert date from string to datetime object
                date = datetime.strptime(row['sampledate'], "%Y-%m-%d %H:%M:%S.%f")  # Adapt date format if needed
                
                temperatures.append(float(row['temperature']))
                humidities.append(float(row['humidity']))
                dates.append(date)

        # Creating a line chart
        line_chart = pygal.Line(x_label_rotation=20)
        line_chart.title = 'Temperature and Humidity over Time'
        line_chart.x_labels = dates
        line_chart.add('Temperature', temperatures)
        line_chart.add('Humidity', humidities)

        # Save the svg to a file
        line_chart.render_to_file('line_chart.svg')

                         
    def cleanup(self):
        """
        resetts all the GPIO Pins after the programm crashed
        """
        self.default_program()
        GPIO.cleanup()



@dataclass
class Conditions:
    """
    representation of Conditions the chamber can have
    """
    temperature : int
    humidity : int
    enddate : datetime 



class ChatBox():    
    """
    chatbot representation of fermentation chamber
    takes a Fermenter Object to interact with 
    """
    def __init__(self, json, fermenter, connection_url, token):
        # takes Fermenter Object 
        self.fermenter = fermenter
        self.json = json
        self.dict_messages = json['data']
        self.ultraAPIUrl = str(connection_url)
        self.token = str(token)

   
    def send_requests(self, type, data):
        """
        stay away
        """
        url = f"{self.ultraAPIUrl}{type}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        return answer.json()
    

    def send_message(self, chatID, text):
        """
        can be used to send a message to a chatID, takes a string as text
        """
        if chatID == "unknown":
            chatID = self.dict_messages["from"]
        data = {"to" : chatID,
                "body" : text}  
        answer = self.send_requests('messages/chat', data)
        return answer
    
    
    def processingـincomingـmessages(self):
        """
        default response vehicle for incoming "fermenter"
        chat requests
        """
        message = self.dict_messages
        text = message["body"].lower()
        chatID = message["from"]
        match = re.search(r"^(ferment)\b.*\b(set \w*|conditions|turn off|turn on|targets|history)\b.*\-\s*(\d*)", text)
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
                
                elif match.group(2) == "history":
                    image = self.fermenter.datalog()
                    return self.send_image(chatID, image)
                
            except ValueError:
                return self.send_message(chatID, f"specified numeric value for {match.group(2)} wasn't specified correctly\nUse Numeric values without any extra Symbols")
        elif (attempt := re.search(r"^(ferment|fermentation)", text)):
            return self.send_message(chatID,"Fermentation Chamber Please type one of these commands: *ferment* + \n*set temp- ?* \n*set temp- ?*\n*set humidity- ?*\n*set duration- ?*\n*turn off-*\n*conditions-*\n*set vent- ?*\n*Avoid any °C, % or other Symbols*\nfor example to set the temperature to 25 Degrees, the command woould be *ferment set temp- 25*")
        elif re.search(r"^sesam öffne dich", text):
            return self.send_message(chatID, "Schlüssel auf Strasse geworfen")


if __name__== "__main__":
    main()
