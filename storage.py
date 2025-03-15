from pydantic import BaseModel
import json
import datetime

class Sharkemon(BaseModel):
    protocol: str
    port: int
    dateFound: datetime.datetime
    desc: str

smon = Sharkemon(protocol="TCP", port=443, dateFound=datetime.datetime.now(), desc="Hi! I'm HTTPS and I like to transport things securely!")
json_smon = smon.model_dump_json()
print(json_smon)
print(smon.protocol)