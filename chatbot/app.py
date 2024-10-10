from flask import Flask, request, jsonify
from fermentationbox import Fermenter, ChatBox
import json

app = Flask(__name__)

fermenter = Fermenter()


connection_url = "https://api.ultramsg.com/instance54183/"
token = "rqqfbcl19puuho4x"

@app.route('/', methods=['POST'])
def home():
    if request.method == 'POST':
        bot = ChatBox(request.json, fermenter=fermenter, connection_url=connection_url, token=token)
        if problem_report := fermenter.problemreport():
            return bot.send_message("unkown", problem_report)

        response = bot.processingـincomingـmessages()

        return response

if(__name__) == '__main__':
    app.run()