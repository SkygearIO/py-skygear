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
def generate_daily_report():
    // do something
    return

@ourd.every("0 0 0 1 * *")
def generate_monthly_report():
    // do something
    return


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
```
