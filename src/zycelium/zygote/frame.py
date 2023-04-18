"""
Zygote Frame.
"""
import json
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Frame(BaseModel):
    kind: str
    name: str
    data: Optional[dict] = None
    meta: Optional[dict] = None
    time: Optional[datetime] = None
    uuid: Optional[UUID] = None

    def to_dict(self) -> dict:
        return {k:v for k, v in self.dict().items() if v}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, frame_json) -> "Frame":
        frame_dict = json.loads(frame_json)
        return cls(**frame_dict)
