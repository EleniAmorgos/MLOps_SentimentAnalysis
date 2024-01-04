FROM python:3.8

ADD requirements.txt ./

RUN pip install --upgrade pip && pip install beautifulsoup4 pandas boto3 requests s3fs

ENV LOG=1

ADD accessKeys.csv /scrap/accessKeys.csv

ADD last30days.py /scrap/last30days.py

EXPOSE 8000

VOLUME /$HOME/scrapp/scrapping

WORKDIR /scrap/

CMD python3 last30days.py
