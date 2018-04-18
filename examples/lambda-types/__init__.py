import skygear
from skygear.models import Location, Record, RecordID


@skygear.op('hello')
def hello():
    """
    This lamda returns some skydb types to the caller. This demonstrates
    the lambda can return skydb types.

    ```
    curl -X "POST" "http://localhost:3000" \
         -H 'Content-Type: application/json; charset=utf-8' \
         -d $'{
      "api_key": "secret",
      "action": "hello"
    }'
    ```
    """
    return [
        1,
        2,
        True,
        "hello",
        Location(1, 2),
        Record(
            id=RecordID("note", "99D92DBA-74D5-477F-B35E-F735E21B2DD5"),
            owner_id="OWNER_ID",
            acl=None,
            data={
                "content": "Hello World!",
            }
        ),
        {
            'location': Location(1, 2)
        }
    ]


@skygear.op('echo')
def echo(value):
    """
    This lamda copies the lambda value and return it to the caller.

    ```
    curl -X "POST" "http://localhost:3000" \
         -H 'Content-Type: application/json; charset=utf-8' \
         -d $'{
      "api_key": "secret",
      "action": "echo",
      "args": [
        {
          "location": {"$lng":1,"$type":"geo","$lat":2}
        }
      ]
    }'
    ```
    """
    return value
