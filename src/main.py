# Third-party imports
import openai
from fastapi import FastAPI, Form, Depends, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Import BuyerGPT
from src.buyergpt import BuyerGPT
from src.transcriber import Transcriber

# Internal imports
from src.utils import send_message, logger

# Commands for running
# uvicorn src.main:app --reload

app = FastAPI()
buyergpt = BuyerGPT()
transcriber = Transcriber()

@app.get("/")
async def index():
    return {"msg": "working"}

@app.post("/message")
async def reply(request: Request):
    # Extract the phone number from the incoming webhook request
    form_data = await request.form()
    whatsapp_number = form_data['From'].split("whatsapp:")[-1]
    print(f"Sending the ChatGPT response to this number: {whatsapp_number}")
    human_input = form_data['Body']

    # Check audio message case
    try:
        media_url = form_data['MediaUrl0']
        media_type = form_data['MediaContentType0']
        print(f"Media URL: {media_url}\nMedia Content type: {media_type}")
        if 'audio/ogg' in media_type:
            human_input = transcriber.transcribe(media_url)
    except:...

    # In case the user request is about offers, send a message for him saying to wait for your response
    if 'offers' in buyergpt._identify_domain(human_input=human_input):
        input_language = buyergpt.translator.detect_language(buyergpt.llm, human_input)
        waiting_message = buyergpt.translator.translate(buyergpt.llm, 'Understood, I will get back to you in a few moments. Please wait, thank you.', destination_language=input_language)
        send_message(whatsapp_number, waiting_message)
    
    print("Human Input is:", human_input)
    # Call the OpenAI API to generate text with BuyerGPT
    response = buyergpt.run(human_input=human_input)

    # The generated text 
    send_message(whatsapp_number, response)
    return ""
