![Skygear Logo](.github/skygear-logo.png)

# Python plugin runtime for Skygear

[![PyPI](https://img.shields.io/pypi/v/skygear.svg)](https://pypi.python.org/pypi/skygear)
[![Build Status](https://travis-ci.org/SkygearIO/py-skygear.svg)](https://travis-ci.org/SkygearIO/py-skygear)
[![License](https://img.shields.io/pypi/l/skygear.svg)](https://pypi.python.org/pypi/skygear)

When the Skygear Server calls your plugin, `py-skygear` will take the plugin message and calls the appropriate function automatically.

## Documentation
The full documentation for Skygear is available on our docs site. The [Plugin get started guide](https://docs.skygear.io/plugin/guide) is a good place to get started.

## Install py-skygear

Install py-skygear by using pip.

```
$ pip install py-skygear
```

Alternatively, you can install `py-skygear` from source by cloning `py-skygear` from this official repository.

Please see the detail installation guide at the [docs site](https://docs.skygear.io/cloud-code/guide).

## Development

Skygears support three kind of protocol for different use case, make sure you add support to all of them or raise appropriate exception.

Supported protocols: `exec`, `http` and `zmq`

If you want to use zmq, you need to install pyzmq, and respective cbinding.
You can install via homebrew in OSX `brew install zeromq`

During development, the easiest way is to debug your plugin using command line:

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


## Support

For implementation related questions or technical support, please refer to the [Stack Overflow](http://stackoverflow.com/questions/tagged/skygear) community.

If you believe you've found an issue with Skygear JavaScript SDK, please feel free to [report an issue](https://github.com/SkygearIO/py-skygear/issues).


## How to contribute

Pull Requests Welcome!

We really want to see Skygear grows and thrives in the open source community.
If you have any fixes or suggestions, simply send us a pull request!


## License & Copyright

```
Copyright (c) 2015-present, Oursky Ltd.
All rights reserved.

This source code is licensed under the Apache License version 2.0 
found in the LICENSE file in the root directory of this source tree. 
An additional grant of patent rights can be found in the PATENTS 
file in the same directory.

```
