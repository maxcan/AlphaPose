ARG  BASE_TAG=latest
FROM 840787491930.dkr.ecr.us-west-2.amazonaws.com/ap_karada_base:${BASE_TAG}

COPY ./*.py /app/
RUN python3 -m py_compile /app/aws.py
RUN python3 -m py_compile /app/fn.py
RUN python3 -m py_compile /app/karada.py

CMD python3 aws.py
