FROM francoisgervais/opencv-python:4.3.0
#FROM jjanzic/docker-python3-opencv
#FROM python:3.6-alpine

LABEL maintainer="Damian Kelly" \
      description="Component to detect faces in images"

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app
ADD https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml /app/haarcascade_frontalface_default.xml

CMD ["python3", "-u", "main.py"]
