FROM python:3.4

RUN \
    wget https://github.com/Yelp/dumb-init/releases/download/v1.0.0/dumb-init_1.0.0_amd64.deb && \
    dpkg -i dumb-init_*.deb && \
    rm dumb-init_*.deb

RUN ( \
    cd /tmp; \
    git clone https://github.com/SkygearIO/py-skygear.git; \
    cd py-skygear; \
    pip install --no-cache-dir -r requirements.txt; \
    python setup.py install; \
    rm -rf /tmp/py-skygear; \
    )

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED 0
ENTRYPOINT ["dumb-init"]
CMD ["py-skygear"]

ONBUILD COPY requirements.txt /usr/src/app/
ONBUILD RUN pip install --no-cache-dir -r requirements.txt

ONBUILD COPY . /usr/src/app


