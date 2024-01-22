FROM python:3.8

ADD requirements.txt ./

RUN pip install --upgrade pip  && pip install -r requirements.txt && python3 -m nltk.downloader punkt && python3 -m nltk.downloader wordnet && python3 -m nltk.downloader stopwords

ENV LOG=1

ADD accessKeys.csv /preprocessing/accessKeys.csv

ADD last30days_retired.py /preprocessing/last30days_retired.py

EXPOSE 8000

VOLUME /$HOME/preprocessing/

WORKDIR /preprocessing/

CMD python3 last30days_retired.py
