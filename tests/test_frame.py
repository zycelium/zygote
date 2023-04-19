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
    now = datetime.now()
    frame = Frame(
        kind="event",
        name="test",
        data={"hello": "world"},
        meta={"test": "this"},
        time=now,
        uuid=uuid,
    )
    assert frame.name == "test"
    assert frame.kind == "event"
    assert frame.data == {"hello": "world"}
    assert frame.meta == {"test": "this"}
    assert frame.time == now
    assert frame.uuid == uuid


def test_frame_to_and_from_json():
    now = datetime.utcnow()
    uuid = uuid4()

    frame_dict = {
        "kind": "event",
        "name": "test",
        "time": now.isoformat(),
        "uuid": str(uuid),
    }
    frame_json = json.dumps(frame_dict)
    frame = Frame(**frame_dict)
    assert frame_json == frame.to_json()

    frame2 = Frame.from_json(frame_json)
    assert frame2.kind == "event"
    assert frame2.name == "test"
    assert frame2.time == now
    assert frame2.uuid == uuid

    assert frame2.json(exclude_unset=True) == frame_json


def test_frame_reply():
    now = datetime.utcnow()
    uuid = uuid4()

    frame = Frame(kind="event", name="test", time=now, uuid=uuid)
    reply = frame.reply(name="test", data={"hello": "world"})
    assert reply.kind == "event"
    assert reply.name == "test"
    assert reply.data == {"hello": "world"}
    assert reply.meta is None
    assert reply.time is None
    assert reply.uuid is None

    reply2 = frame.reply(name="test", data={"test": "this"})
    assert reply2.kind == "event"
    assert reply2.name == "test"
    assert reply2.data == {"test": "this"}
    assert reply2.meta is None
    assert reply2.time is None
    assert reply2.uuid is None

