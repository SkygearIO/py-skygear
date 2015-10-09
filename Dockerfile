FROM python:3.4

ENV PYTHONUNBUFFERED 0

COPY . /tmp/pyourd

RUN (cd /tmp/pyourd; python setup.py install) && rm -rf /tmp/pyourd

