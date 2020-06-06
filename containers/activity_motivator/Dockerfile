FROM python:3.7-alpine

LABEL maintainer="Damian Kelly" \
      description="Code to apply logic to analysed motion sensor data to decide what to say to the user to motivate healthy activity"

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app

CMD ["python3", "-u", "main.py"]
