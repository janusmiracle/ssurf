from dataclasses import dataclass, field
from typing import List


@dataclass
class ReaderOptions:
    """User options for WAVE reading."""

    to_dict: bool = True
    purge: bool = True
    ignore_chunks: List[str] = field(default_factory=List)
