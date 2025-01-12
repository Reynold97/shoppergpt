FROM python:3.9

WORKDIR /buyergpt

COPY ./requirements.txt /buyergpt/requirements.txt

# Install ffmpeg
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y ffmpeg

RUN pip install --no-cache-dir --upgrade -r /buyergpt/requirements.txt

COPY ./buyergpt.py /buyergpt/buyergpt.py

COPY ./translator.py /buyergpt/translator.py

COPY ./utils.py /buyergpt/utils.py

COPY ./transcriber.py /buyergpt/transcriber.py

COPY ./streamlit_chat_ui.py /buyergpt/streamlit_chat_ui.py

COPY ./main.py /buyergpt/main.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6070"]