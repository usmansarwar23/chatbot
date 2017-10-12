import sys, json, requests
from flask import Flask, request, Response
import logging
from googletrans import Translator
import os
#import pandas as pd
#from pandas import compat
import string
#from nltk import word_tokenize
#from nltk.corpus import stopwords

''' load dataset for standardization '''
#file1 = open("data.csv", encoding = "utf8")
#file = list(file1)	#saves dataset as list

# loading Dictionary
#with open('/home/usman/chatbot/Dictionary.pickle', 'rb') as handle:
#    dictionaryRomanUrdu = pickle.load(handle)

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
                    #standardized_text = standardize_message_text(message_text)

                    translated_message_text = google_translate(message_text)
                    #stop = set(stopwords.words('english'))
                    #translated_message_text=[i for i in translated_message_text.lower().split() if i not in stop]
                    #translated_message_text="".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in translated_message_text]).strip()
                    userTest=parse_user_message(translated_message_text)
                    send_message_response(sender_id, userTest)
    logger.info(message_text)
    #logger.info("\\n")
    #logger.info(standardized_text)
    var = message_text
    f=open('log.txt','a+')
    var ='\n' + '\nINPUT \n' +  var + '\n' + 'FROM GOOGLE TRANSLATE' + '\n'+ \
          translated_message_text + '\n' + 'RESPONSE FROM API.AI' + '\n' + userTest
    f.write(var)
    f.close()
    logger.info("\\n")
    logger.info(translated_message_text)
    logger.info("\\n")
    logger.info(userTest)



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

#def standardize_message_text(text):

    #sms='kia aadatein aaaaaaaaaaaa aachi'
#    tokenizedWords = nltk.word_tokenize(text)

#    for word in tokenizedWords:
#        for key, value in dictionaryRomanUrdu.items():
#            if(word in value):
#                indexInList=tokenizedWords.index(word)
#                tokenizedWords[indexInList]=key

#    sentence="".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in tokenizedWords]).strip()
#    return sentence

if __name__ == '__main__':
    app.run(port=8080)
