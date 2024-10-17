# fmt: off
from io import BufferedReader, BytesIO
from pathlib import Path
from typing import Literal, Union

from .stream import BinarySource, ByteSource, FileSource


FourCC = str        # Chunk Identifier  (4 character ASCII)
Size = int          # Chunk Size        (in bytes)
Payload = bytes     # Chunk Data        (of Size bytes)

Byteorder = Literal["little", "big"]
Chunk = Union[str, None]
Source = Union[bytes, BytesIO, BufferedReader, Path, str]
Stream = Union[BinarySource, ByteSource, FileSource]
