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
def auto_assignment(booking, original_booking, db_conn): # booking is record
    return "No Booking"
    table = db_conn.query("table").filter(status="free").first()
    if table:
        booking.table = create_ref(table.record_id)
    else:
        raise ODError("Don't save me")
    return booking


@ourd.before_save("_user", async=False)
def prevent_dead(user, original_user, db_conn):
    return user
    return "Can't dead"


@ourd.before_delete("_user", async=False)
def prevent_dead(user, db_connn):
    raise Exception("can't dead")


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

```

if __name__ == "__main__":
    ourd.stdin()

Run following will be asyncio process and bind to 0mq

You need to install pyzmq, and respective cbinding


OSX -> `brew install zeromq`

```
DATABASE_URL=postgresql://localhost/ourd?sslmode=disable pyourd sample.py --ourd-address 0.0.0.0:3000

```


Debugging your plugin using command line:

```
pyourd sample.py --subprocess init
pyourd sample.py --subprocess op hello:word
pyourd sample.py --subprocess handler chima:echo < README.md
pyourd sample.py --subprocess hook booking:beforeSave
pyourd sample.py --subprocess hook _user:beforeDelete
pyourd sample.py --subprocess timer plugin.generate_daily_report
pyourd sample.py --subprocess timer plugin.generate_monthly_report
```

Since database url is read from environment variable, you have to start Ourd specifying the database connection string:

```
DATABASE_URL=postgresql://localhost/ourd?sslmode=disable ourd development.ini
```
