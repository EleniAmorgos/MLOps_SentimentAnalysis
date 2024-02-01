FROM python:3.8

COPY . /files

RUN pip install --upgrade pip  && pip install -r /files/requirements.txt

ENV LOG=1

ADD accessKeys.csv /files/accessKeys.csv

EXPOSE 8006

RUN mkdir /files/share

WORKDIR /files

CMD python3 model_dtc_0_1.py