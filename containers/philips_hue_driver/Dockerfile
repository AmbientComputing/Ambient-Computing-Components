FROM python:3.7-alpine

LABEL maintainer="Damian Kelly" \
      description="Code for collecting data from Philips Hue"

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app

VOLUME ["data"]

CMD ["python3", "-u", "main.py"]
