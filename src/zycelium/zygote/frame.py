"""
Zygote Frame.
"""
from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class Frame(BaseModel):
    """Zygote Frame."""

    kind: str
    name: str
    data: Optional[dict] = None
    meta: Optional[dict] = None
    time: Optional[datetime] = None
    uuid: Optional[UUID] = None
    reply_to: Optional[UUID] = None

    @classmethod
    def from_json(cls, frame_json) -> "Frame":
        """Parse a JSON string into a Frame."""
        return cls.parse_raw(frame_json)

    @classmethod
    def from_dict(cls, frame_dict) -> "Frame":
        """Parse a dict into a Frame."""
        return cls(**frame_dict)

    def to_json(self) -> str:
        """Convert a Frame to a JSON string."""
        return self.json(exclude_unset=True)

    def to_dict(self) -> dict:
        """Convert a Frame to a dict."""
        return self.dict(exclude_unset=True)

    def reply(
        self,
        kind: Optional[str] = None,
        name: Optional[str] = None,
        data: Optional[dict] = None,
        meta: Optional[dict] = None,
        time: Optional[datetime] = None,
        uuid: Optional[UUID] = None,
    ) -> "Frame":
        """
        Create a reply Frame.

        Reply is a shortcut to link frames together
        to track the cause for current frame being sent.

        """
        kwargs = {
            "kind": kind,
            "name": name,
            "data": data,
            "meta": meta,
            "time": time,
            "uuid": uuid,
        }
        original = {k: v for k, v in self.dict().items() if k not in ["time", "uuid"]}
        kwargs = {**original, **kwargs}
        kwargs["reply_to"] = self.uuid
        return Frame(**kwargs)
