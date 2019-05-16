FROM nvidia/cuda:9.2-cudnn7-devel-ubuntu16.04
RUN mkdir /app
WORKDIR /app
RUN apt-get update
# RUN apt-get install -y software-properties-common
# RUN add-apt-repository ppa:deadsnakes/ppa
# RUN apt-get update
RUN apt-get install -y python3-pip python3 libglib2.0-0 git 
RUN pip3 install --upgrade pip
# AFter this, only use pip not pip3
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY PoseFlow /app/PoseFlow
COPY ./*.py /app/
COPY SPPE /app/SPPE
COPY train_sppe /app/train
COPY yolo /app/yolo
COPY models /app/models
RUN apt-get update
RUN apt-get install -y libsm6 libxext6 x264 libx264-dev
RUN apt-get install -y libxrender-dev
RUN apt-get install -y ffmpeg

