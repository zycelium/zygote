"""
Frame.
"""
from dataclasses import dataclass, field, asdict


@dataclass
class Frame:
    """Frame."""

    name: str
    kind: str
    data: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, frame_dict: dict) -> "Frame":
        """Create frame from dict."""
        return cls(**frame_dict)

    def to_dict(self):
        """Return dict representation of frame."""
        return asdict(self)
    
    def sio_name(self):
        """Return sio name."""
        return f"{self.kind}-{self.name}"

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self)
