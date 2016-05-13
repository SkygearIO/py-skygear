Python plugin runtime for Skygear

[![PyPI](https://img.shields.io/pypi/v/skygear.svg)](https://pypi.python.org/pypi/skygear)
[![Build Status](https://travis-ci.org/SkygearIO/py-skygear.svg)](https://travis-ci.org/SkygearIO/py-skygear)
[![License](https://img.shields.io/pypi/l/skygear.svg)](https://pypi.python.org/pypi/skygear)

For usage guideline, please refer to: http://docs.skygear.io/plugin/guide

### Development and Contribution

Skygear support three kind of protocol for different use case, make sure you
add support to all of them or raise appropriate exception.

Protocol support: `exec`, `http` and `zmq`

If you want to use zmq, you need to install pyzmq, and respective cbinding.
In OSX -> `brew install zeromq`

During development, easiest way is to debug your plugin using command line:

```
export DATABASE_URL=postgres://127.0.0.1/skygear?sslmode=disable
export PUBSUB_URL=ws://localhost:3000/pubsub
echo "{}" | py-skygear sample.py --subprocess init
echo "{}" | py-skygear sample.py --subprocess op hello:word
py-skygear sample.py --subprocess handler chima:echo < record.json
py-skygear sample.py --subprocess hook book:beforeSave < record.json
echo "{}" | py-skygear sample.py --subprocess timer plugin.generate_monthly_report
```

Or you may run a long running process that hook with your own skygear-serve
instance.
```
DATABASE_URL=postgresql://localhost/skygear?sslmode=disable \
py-skygear sample.py \
--skygear-address tcp://127.0.0.1:5555 \
--skygear-endpoint http://127.0.0.1:3000 \
--apikey=API_KEY
```
