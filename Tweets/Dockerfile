FROM python:3.8-slim-buster

WORKDIR /twiiter_coll

COPY . /twiiter_coll

RUN pip3 install -r requirements.txt

CMD [ "python3", "app_tweet.py"]
