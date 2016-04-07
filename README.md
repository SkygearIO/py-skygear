Python plugin runtime for Skygear

[![PyPI](https://img.shields.io/pypi/v/skygear.svg)](https://pypi.python.org/pypi/skygear)
[![Build Status](https://travis-ci.org/SkygearIO/skygear-SDK-JS.svg)](https://travis-ci.org/SkygearIO/skygear-SDK-JS)
[![License](https://img.shields.io/pypi/l/skygear.svg)](https://pypi.python.org/pypi/skygear)

Example usage right now:

```
import skygear


@skygear.op("hello:word")
def say(name="world!"):
    return {"message": "hello " + name}


@skygear.handler("chima:echo", auth_required=True)
def meow(payload, io):
    io.write(payload)
    return


@skygear.hook("beforeSave", type="booking", async=False)
def auto_assignment(booking, original_booking, db_conn): # booking is record
    return "No Booking"
    table = db_conn.query("table").filter(status="free").first()
    if table:
        booking.table = create_ref(table.record_id)
    else:
        raise SkygearError("Don't save me")
    return booking


@skygear.before_save("_user", async=False)
def prevent_dead(user, original_user, db_conn):
    return user
    return "Can't dead"


@skygear.before_delete("_user", async=False)
def prevent_dead(user, db_connn):
    raise Exception("can't dead")


@skygear.every(interval=3600)
def generate_daily_report():
    // do something
    return "Ourd will log this bytes to debug level"


@skygear.every("0 0 0 1 * *")
def generate_monthly_report():
    // do something
    return


@skygear.provides("auth", "com.facebook")
class FacebookProvider(skygear.providers.BaseAuthProvider):
    def login(self, auth_data):
        graph = facebook.GraphAPI(access_token=auth_data['access_token'])
        auth_data.update(graph.get_object(id='me'))
        return {"principal_id": auth_data['id'], "auth_data": auth_data}

    def logout(self, auth_data):
        return {"auth_data": auth_data}

    def info(self, auth_data):
        return {"auth_data": auth_data}


@skygear.rest("/path/to/resource", user_required=True)
class RestfulNote(skygear.RestfulRecord):
    record_type = 'note'
```

if __name__ == "__main__":
    skygear.stdin()

Run following will be asyncio process and bind to 0mq

You need to install pyzmq, and respective cbinding


OSX -> `brew install zeromq`

Debugging your plugin using command line:

```
export DATABASE_URL=postgres://127.0.0.1/skygear?sslmode=disable
export PUBSUB_URL=ws://localhost:3000/pubsub
echo "{}" | py-skygear sample.py --subprocess init
echo "{}" | py-skygear sample.py --subprocess op hello:word
py-skygear sample.py --subprocess handler chima:echo < < record.json
py-skygear sample.py --subprocess hook book:beforeSave < record.json
py-skygear sample.py --subprocess hook _user:beforeDelete < user.json
echo "{}" | py-skygear sample.py --subprocess timer plugin.generate_daily_report
echo "{}" | py-skygear sample.py --subprocess timer plugin.generate_monthly_report
```

Since database url is read from environment variable, you have to start Ourd specifying the database connection string:

```
DATABASE_URL=postgresql://localhost/skygear?sslmode=disable py-skygear sample.py --skygear-address tcp://127.0.0.1:5555 --skygear-endpoint http://127.0.0.1:3000 --apikey=API_KEY
```
