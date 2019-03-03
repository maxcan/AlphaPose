FROM nvidia/cuda:9.2-cudnn7-devel
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN apt-get update
RUN apt-get install -y python3-pip python3
RUN apt-get install -y git

RUN pip3 install -r requirements.txt
COPY PoseFlow /app/PoseFlow
COPY ./*.py /app/
COPY SPPE /app/SPPE
COPY train_sppe /app/train
COPY yolo /app/yolo
COPY models /app/models
RUN apt-get install -y libsm6 libxext6
RUN apt-get install -y libxrender-dev

CMD python3 aws.py
