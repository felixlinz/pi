import json
import requests
import datetime

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

    def send_image(self, chatID):
        data = {"to" : chatID,
                "image" : "https://file-example.s3-accelerate.amazonaws.com/images/test.jpeg"}  
        answer = self.send_requests('messages/image', data)
        return answer

    def temperature(self, chatID, text):
        temperature = text
        return f"Temperature set to {int(temperature)}"

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


    def Processingـincomingـmessages(self):
        if self.dict_messages != []:
            message =self.dict_messages
            text = message['body'].split("-")
            if not message['fromMe']:
                chatID  = message['from'] 
                if text[0].lower() == 'set temp':
                    return self.temperature(chatID,text[1])
                elif text[0].lower() == 'humidity -':
                    return self.humidity(chatID)
                elif text[0].lower() == 'duration -':
                    return self.duration(chatID)
                else:
                    return self.welcome(chatID, True)
            else: return 'NoCommand'