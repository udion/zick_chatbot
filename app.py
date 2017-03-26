import os
import sys
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
app = Flask(__name__)


@app.route('/', methods=['GET'])

def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200


@app.route('/', methods=['POST'])

def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                                                         # someone sent us a messag
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    movie_cat=['comedy','action','thriller','sci_fi','horror','drama','romance']
                    song_cat=['rap','r-and-b','pop','dance-club-play','latin','jazz']
                    article_cat=['technology', 'business','fashion', 'sport', 'environment', 'travel', 'culture', 'commentisfree']

                    if message_text.lower() in movie_cat:
                        processmoviegenre(message_text,sender_id)
                    if message_text.lower() in song_cat:
                        processsonggenre(message_text,sender_id)
                    if message_text.lower() in article_cat:
                        processartgenre(message_text,sender_id)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass    
                if messaging_event.get("optin"):  # optin confirmation
                    pass
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass
    return "ok", 200


def send_message(recipient_id, message_text):
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }

    headers = {
        "Content-Type": "application/json"
    }

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)



def processmoviegenre(genre, sid):
    url="http://www.imdb.com/genre/"
    r = requests.get(url+genre.lower()+'/')
    soup = BeautifulSoup(r.content)

    msg = "Aah, I see you have taste for "+genre.lower()+" \n maybe you should try the following they've top ratings at IMDB"
    send_message(sid, msg)
    res = soup.find_all("table",{"class": "results"})
    #the point in html page below which we get data
    #Now to get only the film names, the pattern was
    #'/title/tt' in the href of the anchor tag <a>
    for item in res:
        for link in item.find_all('a'):
            if 'title/tt' in link.get('href',''):
                if link.text != 'X':
                    send_message(sid, link.text)
    send_message(sid, "Hey, hope you got what you were looking for, you can always click on options to explore more")


def processsonggenre(genre,sid):
    url="http://www.billboard.com/charts/"
    r = requests.get(url+genre.lower()+'-songs')
    soup = BeautifulSoup(r.content)
    res = soup.find_all('h2', {'class': 'chart-row__song'})
    #Here we have extracted all the headers of the different songs available on the billboard
    for item in res:
        send_message(sid, item.text)
    send_message(sid, "Hey, hope you got what you were looking for, you can always click on options to explore more")

def processartgenre(genre,sid):
    url="https://www.theguardian.com/uk/"
    r = requests.get(url+genre.lower())
    soup = BeautifulSoup(r.content)
    divs = soup.find_all('div',{'class':'headline-list__text'})
    #This point onwards we have the most viewed news of that category
    for div in divs:
        links = div.find_all('a')
        for link in links:
            send_message(sid,link.get('href'))
    send_message(sid, "Hey, hope you got what you were looking for, you can always click on options to explore more")



def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True)