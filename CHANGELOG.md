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
