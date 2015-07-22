Python plugin runtime for Ourd

Example usage right now:


```
import pyourd as ourd


@ourd.op("hello:word")
def say(name="world!"):
    return {"message": "hello " + name}


@ourd.handler("chima:echo", auth_required=True)
def meow(payload, io):
    io.write(payload)
    return


@ourd.hook("beforeSave", type="booking", async=False)
def auto_assignment(booking, db_conn): # booking is record
    return "No Booking"
    table = db_conn.query("table").filter(status="free").first()
    if table:
        booking.table = create_ref(table.record_id)
    else:
        raise ODError("Don't save me")
    return booking


@ourd.hook("beforeDelete", type="_user", async=False)
def prevent_dead(user, db_conn):
    return "Can't dead"

@ourd.every(interval=3600)
def generate_daily_report(io):
    io.write("Ourd will see this bytes")
    // do something
    return

@ourd.every("0 0 0 1 * *")
def generate_monthly_report(io):
    // do something
    return


@ourd.provides("auth", "com.facebook")
class FacebookProvider(pyourd.providers.BaseAuthProvider):
    def login(self, auth_data):
        graph = facebook.GraphAPI(access_token=auth_data['access_token'])
        auth_data.update(graph.get_object(id='me'))
        return {"principal_id": auth_data['id'], "auth_data": auth_data}

    def logout(self, auth_data):
        return {"auth_data": auth_data}

    def info(self, auth_data):
        return {"auth_data": auth_data}


if __name__ == "__main__":
    ourd.stdin()

```

Run following:

```
python sample.py init
python sample.py op hello:word
python sample.py handler chima:echo < README.md
python sample.py hook booking:beforeSave
python sample.py hook _user:beforeDelete
python sample.py timer __main__.generate_daily_report
python sample.py timer __main__.generate_monthly_report
```
