FROM python:3.8

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8001

CMD uvicorn api_sentiment_analysis_OAuth_logs:api --host 0.0.0.0 --port 8001
