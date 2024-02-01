FROM python:3.9

COPY . /files/

RUN pip install --upgrade pip  && pip install -r /files/requirements.txt

ENV LOG=1

EXPOSE 8501

WORKDIR /files/

CMD ["streamlit", "run", "streamlit-satisfaction4.py"]