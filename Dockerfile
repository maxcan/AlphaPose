FROM python:3.7

RUN mkdir /app
ADD PoseFlow /app/
ADD ./*.py /app/
ADD SPPE /app/
ADD train_sppe /app/
ADD yolo /app/
ADD models /app/
ADD requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
