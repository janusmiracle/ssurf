from io import BufferedReader, BytesIO
from pathlib import Path

from ._types import Source, Stream
from .stream import BinarySource, ByteSource, FileSource


def normalize_stream(source: Source) -> Stream:
    """Normalizes source input into a stream."""

    if isinstance(source, (BufferedReader, BytesIO)):
        return BinarySource(source)

    elif isinstance(source, bytes):
        return ByteSource(source)

    elif isinstance(source, (str, Path)) and Path(source).is_file():
        return FileSource(source)

    else:
        raise ValueError(
            f"Invalid source type: {type(source)}. Expected file path, binary source, or bytes."
        )
