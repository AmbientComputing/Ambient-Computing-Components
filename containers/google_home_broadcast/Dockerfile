FROM python:3.7-alpine

LABEL maintainer="Damian Kelly" \
      description="Broadcasts notification messages to user using chrome cast protocol"

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app

CMD ["python3", "-u", "main.py"]
