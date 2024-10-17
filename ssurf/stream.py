import os

from io import BufferedReader, BytesIO
from pathlib import Path
from typing import Protocol, Union


class ReadableStream(Protocol):
    def read(self, size: int = -1) -> bytes: ...

    def seek(self, offset: int = 0, whence: int = 0) -> None: ...

    def tell(self) -> int: ...

    def __len__(self) -> int: ...

    # def reset(self) -> None: ...


class FileSource(ReadableStream):
    def __init__(self, fp: Union[Path, str]):
        self._stream = open(fp, "rb")

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def seek(self, offset: int = 0, whence: int = 0) -> None:
        self._stream.seek(offset, whence)

    def tell(self) -> int:
        return self._stream.tell()

    def close(self) -> None:
        self._stream.close()

    def __len__(self) -> int:
        self._stream.seek(0, os.SEEK_END)
        return self._stream.tell()


class BinarySource(ReadableStream):
    def __init__(self, stream: Union[BytesIO, BufferedReader]):
        self._stream = stream

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def seek(self, offset: int = 0, whence: int = 0) -> None:
        self._stream.seek(offset, whence)

    def tell(self) -> int:
        return self._stream.tell()

    def __len__(self) -> int:
        self._stream.seek(0, os.SEEK_END)
        return self._stream.tell()


class ByteSource(ReadableStream):
    def __init__(self, data: bytes):
        self._stream = BytesIO(data)  # wrap

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def seek(self, offset: int = 0, whence: int = 0) -> None:
        self._stream.seek(offset, whence)

    def tell(self) -> int:
        return self._stream.tell()

    def __len__(self) -> int:
        self._stream.seek(0, os.SEEK_END)
        return self._stream.tell()
