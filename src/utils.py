# Standard library import
import logging
import os
import requests
import urllib.request

# Third-party imports
from twilio.rest import Client
from decouple import config
from pydub import AudioSegment

# Third-party imports
from twilio.rest import Client
from decouple import config
import pyshorteners


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
# Get environment variables using python-decouple
account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")
twilio_number = config("TWILIO_NUMBER")

client = Client(account_sid, auth_token)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sending message logic through Twilio Messaging API
def send_message(to_number, body_text):
    try:
        message = client.messages.create(
            from_=f"whatsapp:{twilio_number}",
            body=body_text,
            to=f"whatsapp:{to_number}"
            )
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")

# Shorten a given shopping url
def shorten_url(url):
    shortener = pyshorteners.Shortener()
    short_url = shortener.dagd.short(url)
    return short_url

def ogg2mp3(audio_url):
    # Get the response of the OGG file
    response = requests.get(audio_url)
    # Get the redirect URL result
    url = response.url # `url` value something like this: "https://s3-external-1.amazonaws.com/media.twiliocdn.com/<some-hash>/<some-other-hash>"
    # Download the OGG file
    urllib.request.urlretrieve(url, "audio.ogg")
    # Load the OGG file
    audio_file = AudioSegment.from_ogg("audio.ogg")
    # Export the file as MP3
    audio_file.export("audio.mp3", format="mp3")
    return os.path.join(os.getcwd(), "audio.mp3")