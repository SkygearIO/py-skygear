FROM python:3.4

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


