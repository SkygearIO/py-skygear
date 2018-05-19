FROM python:3.6-stretch

RUN \
    wget https://github.com/Yelp/dumb-init/releases/download/v1.0.0/dumb-init_1.0.0_amd64.deb && \
    dpkg -i dumb-init_*.deb && \
    rm dumb-init_*.deb

RUN pip install --upgrade pip && \
    pip install --upgrade setuptools

ADD *.whl /tmp/
RUN find /tmp -name "*.whl" -exec pip install --no-cache-dir "{}[zmq]" \;

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED 0
ENTRYPOINT ["dumb-init"]
CMD ["py-skygear"]
