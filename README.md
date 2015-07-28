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

```

Run following will be asyncio process and bind to 0mq

```
pyourd sample.py --ourd-address 0.0.0.0:3000

```


Debugging your plugin using command line

```
pyourd sample.py --subprocess init
pyourd sample.py --subprocess op hello:word
pyourd sample.py --subprocess handler chima:echo < README.md
pyourd sample.py --subprocess hook booking:beforeSave
pyourd sample.py --subprocess hook _user:beforeDelete
pyourd sample.py --subprocess timer plugin.generate_daily_report
pyourd sample.py --subprocess timer plugin.generate_monthly_report
```
