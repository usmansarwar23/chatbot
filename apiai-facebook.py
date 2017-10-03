import sys, json, requests
from flask import Flask, request, Response
import logging
from googletrans import Translator
import os

''' load dataset for standardization '''
file1 = open("data.csv", encoding = "utf8")
file = list(file1)	#saves dataset as list

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

PAT = 'EAACh9MQ3zy8BAJuw2AdCaSezuGIio39aVlFENWK1ZA0LHVEcU3BnhqFRrUJrZAKEfCdp9DZBJa8UAZB0ZCFb7FWtJ6mZAzUVenZCzEcJX8vg7HxEAwgcL93YOfXxZCb9CJygQpMo8J49JR6AGYh67CeoMGZAAs9OZCsUPrhhA19wFmlAZDZD'

VERIFY_TOKEN = 'test'

CLIENT_ACCESS_TOKEN = '3a67ab4afb49424587183ae8b04bf88b'

ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)


@app.route('/', methods=['GET'])
def handle_verification():
    '''
    Verifies facebook webhook subscription
    Successful when verify_token is same as token sent by facebook app
    '''
    if (request.args.get('hub.verify_token', '') == VERIFY_TOKEN):
        logger.info("\\n successfully verified")
        return Response(request.args.get('hub.challenge', ''))
    else:
        logger.info("Wrong verification token!")
        return Response('Error, invalid token')


@app.route('/', methods=['POST'])
def handle_message():
    '''
    Handle messages sent by facebook messenger to the applicaiton
    '''
    data = request.get_json()
    logger.info("\\n")

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"]
                    message_text = messaging_event["message"]["text"]
                    standardized_text = standardize_message_text(message_text)
                    translated_message_text = google_translate(standardized_text)
                    send_message_response(sender_id, parse_user_message(translated_message_text))
    logger.info(message_text)
    logger.info("\\n")
    logger.info(sender_id)
    return "ok"

def google_translate(user_text):
    '''
    this function will translate the received text using google translate
    '''
	
    translator = Translator()
    detected_lang = translator.detect(user_text).lang
	
    if detected_lang == 'en':
        trans_input = user_text
        print(trans_input)
        return trans_input
    else:
        mid_trans = translator.translate(user_text, src="hi", dest = "ur").text
        trans_input = translator.translate(mid_trans, src = "ur", dest = "en").text
        print(trans_input)
        return trans_input

def send_message_response(sender_id, message_text):

    sentenceDelimiter = ". "
    messages = message_text.split(sentenceDelimiter)
    for message in messages:
        send_message(sender_id, message)


def send_message(sender_id, message_text):
    '''
    Sending response back to the user using facebook graph API
    '''
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": PAT},
        headers={"Content-Type": "application/json"},
        data=json.dumps({
        "recipient": {"id": sender_id},
        "message": {"text": message_text}
    }))

def parse_user_message(user_text):
    '''
    Send the message to API AI which invokes an intent
    and sends the response accordingly
    The bot response is appened with weaher data fetched from
    open weather map client
    '''
    
    request = ai.text_request()
    request.query = user_text

    response = json.loads(request.getresponse().read().decode('utf-8'))
    responseStatus = response['status']['code']
	
    if (responseStatus == 200):
        print("API AI response", response['result']['fulfillment']['speech'])
        return (response['result']['fulfillment']['speech'])
    else:
        return ("Sorry, I couldn't understand that question")

def standardize_message_text(text):
    '''
    use the roman urdu dictionary to standardize text and return a standardized message text
    '''
    out_list = ""
    i = 0
	
    while i < len(text):
        word = text[i]
        out_word = 0   
        for line in file:   #checks every line of the urdu dataset against the 'word'
            line = line.split(",")
            for value in line:   
                if word == value:   #checks if word is present in the respective line of the dataset
                    if out_list == "":
                        out_list = out_list + line[0]
                    else:
                        out_list = out_list + " " + line[0]
                    out_word = line[0]
                    break
        if out_word == 0:   #if word is not present in the dataset for normalization, save it to the out_list as it is
            if out_list == "":
                out_list = out_list + word
            else:
                out_list = out_list + " " + word
            #print (word)
        i = i+1
    return out_list   #returns normalized input


if __name__ == '__main__':
    app.run(port=80)
