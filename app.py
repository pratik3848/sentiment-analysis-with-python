from flask import Flask, request
import simplebot as sb
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/")
def home():
    return "<h2>Hello world</h2> Welcome to twily!"


@app.route("/get", methods=['POST'])
def get_bot_response():
    user_input = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    twily_response = sb.escalation(user_input)
    msg.body(twily_response)
    return str(resp)

@app.route("/test")
def bot_response():
    user_input = request.args.get('msg').lower()
    return f'<h2>{sb.escalation(user_input)}'


if __name__ == "__main__":
    app.run()
