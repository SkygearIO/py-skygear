FROM python:3.5

RUN \
    wget https://github.com/Yelp/dumb-init/releases/download/v1.0.0/dumb-init_1.0.0_amd64.deb && \
    dpkg -i dumb-init_*.deb && \
    rm dumb-init_*.deb

RUN pip install --upgrade pip && \
    pip install --upgrade setuptools

COPY requirements.txt /tmp/py-skygear/
RUN pip install --no-cache-dir -r /tmp/py-skygear/requirements.txt

COPY . /tmp/py-skygear
RUN (cd /tmp/py-skygear; pip install ".[zmq]") && rm -rf /tmp/py-skygear

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED 0
ENTRYPOINT ["dumb-init"]
CMD ["py-skygear"]
