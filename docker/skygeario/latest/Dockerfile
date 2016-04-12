FROM python:3.4

RUN \
    wget https://github.com/Yelp/dumb-init/releases/download/v1.0.0/dumb-init_1.0.0_amd64.deb && \
    dpkg -i dumb-init_*.deb && \
    rm dumb-init_*.deb

RUN pip install --upgrade pip && \
    pip install --upgrade setuptools

RUN ( \
    cd /tmp; \
    git clone https://github.com/SkygearIO/py-skygear.git; \
    cd py-skygear; \
    pip install --no-cache-dir -r requirements.txt; \
    pip install ".[zmq]"; \
    rm -rf /tmp/py-skygear; \
    )

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED 0
ENTRYPOINT ["dumb-init"]
CMD ["py-skygear"]
