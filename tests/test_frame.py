# pyright:  reportGeneralTypeIssues=false
# pylint: disable=no-member, missing-function-docstring, missing-module-docstring
import json
from datetime import datetime
from uuid import uuid4

from zycelium.zygote import Frame


def test_frame_defaults():
    frame = Frame(kind="event", name="test")
    assert frame.name == "test"
    assert frame.kind == "event"
    assert frame.data is None
    assert frame.meta is None
    assert frame.time is None
    assert frame.uuid is None


def test_frame_full():
    uuid = uuid4()
    now = datetime.now().isoformat()
    frame = Frame(kind="event", name="test", data={"hello": "world"}, meta={"test":"this"}, time=now, uuid=uuid)
    assert frame.name == "test"
    assert frame.kind == "event"
    assert frame.data == {"hello": "world"}
    assert frame.meta == {"test": "this"}
    assert frame.time.isoformat() == now
    assert frame.uuid == uuid


def test_frame_to_and_from_json():
    frame_dict = {
        "kind": "event",
        "name": "test",
    }
    frame_json = json.dumps(frame_dict)
    frame = Frame(**frame_dict)
    assert frame_json == frame.to_json()
    
    frame2 = Frame.from_json(frame_json)
    assert frame2.kind == "event"
    assert frame2.name == "test"
    