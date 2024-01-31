FROM ubuntu:20.04

RUN apt-get update && apt-get install python3-pip -y && pip3 install uvicorn pytest requests && rm -rf /var/lib/apt/lists/*

COPY . . 

EXPOSE 8002

CMD uvicorn test_request_api_OAuth:url --host 0.0.0.0 --port 8002
