Welcome to the Fermentation Machine. 
To get started adhere to the following steps. 

To control the raspberrypi use either 
locally : "ssh felixlinz@rasp.local"
remotely : "ssh -p <xxxxx>  felixlinz@<0.tcp.eu.ngrok.io>"

pre: 

1. create instance on "https://user.ultramsg.com/", authenticate via whatsapp etc

2. edit the app.py file in /pi/chatbot to have matching connection url and token as on the website


start app: 

1. start ngrok via "./ngrok http 5000" in home folder
2. new terminal -> navigate to pi/chatbot 
3. start the flask server via "flask run" 
5. copy paste the "Forwardig" link into "Webhook" on the ultramsg page