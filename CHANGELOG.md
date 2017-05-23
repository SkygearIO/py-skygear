## 0.24.0 (2017-04-20)

### Features

- Make plugin transport ZMQ multiplex (SkygearIO/skygear-server#295)
    
    This feature will enable the bidirectional plugin transport and multiplexing.
    
    Calling `send_action` within the plugin will route back to the same worker
    from now on. It is implicit, developer does not need to specific worker reuse
    or not.
    This merge also add dynamic threading at ZMQTransport.
    It solved the problem of workers exhaust problem.

### Bug Fixes

- Fix unable to set envvar to `false` (#137)

## 0.23.0 (2017-04-20)

### Features

- Add user friendly error message to error class SkygearIO/skygear-SDK-Android#89

## 0.22.2 (2017-03-31)

### Features
- Read content type in asset serialisation SkygearIO/skygear-SDK-JS#164

### Bug Fixes
- Update the mock interface for ZMQTransport (#122)

### Other Notes
- Add back the missing boto3 deps at setup.py


## 0.22.0 (2017-02-10)

### Features

- Add timeout parameter to send_action (skygeario/skygear-server#271)

### Bug Fixes

- Fix passing key_required to server (#117)

## 0.21.0 (2017-01-11)

### Features

- Enable sending push notification by topic (SkygearIO/skygear-server#239)

### Other Notes

- Add documentation of `includeme`


## 0.20.0 (2016-12-20)

### Features

- Support s3 asset store url prefix
- Enable zmq thread pool configuration (#76)
- Support asset url signer (#105)
- Add support for UnknownValue type (SkygearIO/skygear-server#231, #101)

### Bug Fixes

- Fix postgis-2.3 not found
- Config module from directory once is loaded if it is specifid in
  options.modules (#70)
- Auto fix static assets prefix if slash is specified (#95)

### Incompatible changes

- Remove `skygear.skyconfig`


## 0.19.0 (2016-11-10)

### Incompatible changes

- The protocol for plugin transport is updated. Skygear Server and cloud code
  in previous versions cannot be used with this version.

### Features

- Support for plugin only request during initialization (SkygearIO/skygear-server#219)
- Support plugin event (#79)
- Add ignore-public-html option

### Bug Fixes

- Fix zmq stopping bug on maintains_worker_count (#80)

### Other Notes

- Fix various issues with docker compose and Makefile
- Handle http plugin request encoded in request body (#82)
- Check opened worker count instead of current active worker


## 0.18.0 (2016-10-28)

### Features

- Make the zmq transmitter open worker thread (#72)
- Provide skygear.config for loading and config of plugin (#70)
- Add settings utility (#62)
- Override previously defined extension points (#58)

### Other Notes

- Push Docker image as `onbuild` also (#66)
- Update to use py3.5 as default release version (#63)


## 0.17.0 (2016-09-15)

### Features

- Load more than one cloudcode entry points (#57)


## 0.16.0 (2016-09-02)

### Bug Fixes

- Fix local static asset not serve correctly during development (#50)

### Other Notes

- Un-deprecate PUBSUB_URL (#52)
- Revamp release process


## 0.15.0 (2016-08-17)

### Other Notes

- Update postgres to 9.5 (#45)
- Update catapi docker-compose to embrace env var config
- Remove the SKYGEAR prefix in envvar (#27)


## 0.14.0 (2016-07-26)

### Features

- send_action support datetime serialization using rfc3339 (#12)
- Add exception_handler decorator(#19)
- Register citext in postgresql dialects (#31)


## 0.13.1 (2016-07-08)

### Features
- Do not serve static assets by default


## 0.13.0 (2016-07-05)

### Features

- Include both api_key and access_token in send_action
- Provide meta attributes like created_by on serialized_record (SkygearIO/chat#23)
- Allow RestfulRecord subclass to provide container
- Implement serving static assets for development (#23)
- Automatically generate ID for restful record
- Enable threading in http transport
- Add function to check if a table exists in schema
- Declare and collect static assets (#21, #22)

### Bug fixes

- Fix handler name with slashes in http transport (#33, oursky/py-skygear#137)
- Fix handler returning werkzeug response

### Other notes

- Fix bcrypt version at 2.0.0 because build failing
- Fix onbuild image not having zmq transport installed


## 0.12.0 (2016-05-30)

### Other Notes
 - Correct the Travis-CI link in README.md
 - Remove the wrong information at README
 - Point user to the doc site.
 - Left development and contribution for advance dev.


## 0.11.0 (2016-05-01)

### Features
- Set the container default before loading source
  - Problem:
    When a user want to send_action to Skygear on bootsrtap, he will try to
    instantiate a SkygearContianer instance. However the skygear container
    is not yet loaded the default config from environment variable. It make the
    developer have to load it from the environment by themselves.

  - Fix:
    Set the container default before attempting to load the plugin source, when
    loading the plugin source. Developer got a SkygearContainer with proper
    defaults.
- Add Public ACE support

### Bug Fixes
- Raise exception with proper message if no pyzmq (#13)
- Make log level respect env SKYGEAR_LOGLEVEL

### Other Notes
- Update slack notification token (SkygearIO/skygear-server#19)
- Add Github issue tempalte


## 0.10.0 (2016-04-13)

### Features
- Make pyzmq an optional dependency (refs oursky/py-skygear#129)
- Support paging and filtering in restful index
- Implement restful resource (refs oursky/py-skygear#135)

### Bug Fixes
- Update development.ini in catapi
- Change docker-compose on the catapi example
- Remove paging logic from py-skygear
- Reflect database table using SQLAlchemy


## 0.9.0 (2016-03-16)

### Feature

- Implement @skygear.handler #126 #128

## 0.8.0 (2016-03-09)

### Features

- Automatically import plugin file #125

  The plugin source file is now optional. py-skygear will attempt to
  find the plugin source file in the working directory.

## 0.7.0 (2016-03-02)

### Other Notes

- Update the catapi to demo of relative import

## 0.6.0 (2016-02-24)

### Features

- Support roles base ACE serialisation #121
- Support for skygear config passing
- Run lambda function in exec without content
- Add support for impersonating user using master key

## 0.5.0 (2016-02-17)

### Features

- Implement HttpTransport and improve other transports oursky/skygear#537, oursky/skygear#538
- Add support for skygear-style exception #109
- Support registering multiple hooks of same kind #108

### Bug Fixes

- Fi login requirement required by catapi example
- Fix typo in development.ini

### Other Notes

- Added using dumb-init to speed up docker container closing
- Install signal to handle container stop

## 0.4.0 (2016-01-13)

### Feature

- It is now possible to get the current request context from lambda
  and hook. Use the current_user_id() function to get the current User ID
  oursky/skygear#470
- Lambda function can specify whether authenticated user or access key
  is required oursky/skygear#367

## 0.3.0 (2016-01-06)

### Features

- Set API Key to pubsub websocket request #85

### Bug Fixes

- Set search path properly before pass conn to db hook
- Fix response not being returned in Container.send_action #96
- Remove unused parameter at user.reset_password_by_username #93

## 0.2.0 (2015-12-23)

### Bug Fixes

- Fix unable to print formatted string when argument to every decorator is
  invalid

## 0.1.0 (2015-12-16)

### Features

- Add db connection context helper #88
- Add `Record.get`
- Add `exemples/catapi` to illustrate the usage

### Bug Fixes

- Fix cannot find pending_notification table exception
