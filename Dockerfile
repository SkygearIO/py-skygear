FROM python:3.4

ENV PYTHONUNBUFFERED 0

COPY . /tmp/py-skygear

RUN (cd /tmp/py-skygear; python setup.py install) && rm -rf /tmp/py-skygear

