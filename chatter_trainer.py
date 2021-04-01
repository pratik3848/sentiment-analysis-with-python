from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

chatbot = ChatBot("Twily")
trainer = ListTrainer(chatbot)

documentation_topics = [
("sdk", "https://www.twilio.com/docs/sms/whatsapp#sdks"),
("python helper library", "https://www.twilio.com/docs/libraries/python"),
("tutorials", "https://www.twilio.com/docs/sms/whatsapp/tutorial/ send-and-receive-media-messages-twilio-api-whatsapp"),
("autopilot", "https://www.twilio.com/docs/autopilot/channels/whatsapp"),
("contact us", "https://support.twilio.com/hc/en-us")]

twilio_knowledge = [
("Twilio description", "Simply put, Twilio is a developer platform for communications.\
        Software teams use Twilio APIs to add capabilities like voice, video, and messaging \
        to their applications. This enables businesses to provide the right communications \
            experience for their customers."),
("Twilio email", "Sorry, you can submit a ticket at: https://www.twilio.com/console/support/tickets/create"),
("Twilio phone number", "We don't have a phone number for this type of account"),
("mailing address", "You can email our corporate headquarters at hello@craft.com"),
("chatterbot", "library making it easy to generate automated responses to a user's input, visit https://chatterbot.readthedocs.io/en/stable/"),
("textblob", "library for processing textual data, please visit https://textblob.readthedocs.io/en/dev/")
]

classifier = ["silly", "dumb", "stupid", "I'dont think so", "I don't care",
                   "do you know anything", "not good", "omg",
                   "this is bad", "not what I want", "live help",
                   "get me a rep", "I need a real person"]

for topic, link in documentation_topics:
    trainer.train([
        f"{topic}",
        f"Sure, here is the {topic} link: {link}"
    ])

for topic, description in twilio_knowledge:
    trainer.train([
        f"{topic}",
        f"Ok, here is the {topic} information you are looking for: {description}"
    ])

for i in classifier:
    trainer.train([
        f"{i}",
        "I am sorry you feel that way, please ask the question again"
    ])

trainer.export_for_training('twilybot.json')