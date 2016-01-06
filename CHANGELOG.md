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
