import json
import requests
import datetime
import re

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

    def temperature(self, chatID, text):
        return self.send_message(chatID, f"Temperature set to {int(text)}")

    def time(self, chatID):
        t = datetime.datetime.now()
        time = t.strftime('%Y-%m-%d %H:%M:%S')
        return self.send_message(chatID, time)


    def welcome(self,chatID, noWelcome = False):
        welcome_string = ''
        if (noWelcome == False):
            welcome_string = "Fermentation Chamber\n"
        else:
            welcome_string = """
Fermentation Chamber
            
Please type one of these commands:
*set temp- * 
*set humidity- * 
*set duration- *
*turn off*
"""
        return self.send_message(chatID, welcome_string)


    def processingـincomingـmessages(self,text):
        match = re.search(r"^(ferment)\b.*\b(set \w*)\b.*\-\s*(\d*)", text)
        if match:
            try:
                if match.group(2) == "set temp":
                    return f"temperature set to {int(match.group(3))} Degrees"
                elif match.group(2) == "set humidity":
                    return f"humidity set to {int(match.group(3))} Percent Air Wetness"
                elif match.group(2) == "set duration":
                    return f"duration set to {int(match.group(3))} Hours"
            except ValueError:
                return f"specified numeric value for {match.group(2)} wasn't specified correctly\nUse Numeric values without any extra Symbols"
                
        else: 
            attempt = r"^(ferment|fermentation)"
            if attempt:
                return "Fermentation Chamber Please type one of these commands: \n*set temp- ?* \n*set temp- ?*\n*set humidity- ?*\n*set duration- ?*\n*turn off*"