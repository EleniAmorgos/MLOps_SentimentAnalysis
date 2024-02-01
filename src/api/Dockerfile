FROM alpine:3.16

RUN apk add --no-cache python3 py3-pip && pip3 install --no-cache-dir uvicorn fastapi pyjwt pandas tqdm pydantic BeautifulSoup4 asyncio typing fastapi.security pickle5 numpy scikit-learn==1.1.1 && pip3 install --no-cache-dir requests && pip3 install --no-cache-dir passlib && pip3 install --no-cache-dir data && pip3 install --no-cache-dir nltk && pip3 install --no-cache-dir python-multipart

COPY . .

EXPOSE 8001

CMD uvicorn api_sentiment_analysis_OAuth:api --host 0.0.0.0 --port 8001
