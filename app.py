"""
created by diksha singla 08-06-2019
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from utils import fetch_reply
from database import insertdata

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/sms", methods=['POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    print(request.form)
    msg = request.form.get('Body')
    sender=request.form.get('From')

    # Create reply
    resp = MessagingResponse()
    """if utils.get_intentname(msg,sender)=="get_comapny":
        resp.message(fetch_reply(msg,sender)).media(wikipedia.page())"""
    reply_data,msg_data,type_data=fetch_reply(msg,sender)
    if type_data=="type2":
        print(msg_data)
        resp.message(reply_data)
        resp.message(msg_data)
        resp.message("image:").media(msg_data)
    else:
        resp.message(reply_data)
    #resp.message("You said: {}".format(msg))
    #.media("https://images.pexels.com/photos/414612/pexels-photo-414612.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)