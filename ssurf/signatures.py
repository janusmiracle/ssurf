from dataclasses import dataclass

from ._types import Byteorder


@dataclass
class Identity:
    base: str
    container: str
    description: str
    endian: Byteorder


@dataclass
class Signature:
    identity: Identity
    identifier: bytes
    size: int
    offset: int = 0
    soffset: int = 8


# For container formats like RIFF, the master identifier (RIFF, RIFX, RF64 ...)
# is merged with the corresponding form type (WAVE ...) into a single byte string.
# For example, the first entry in SIGNATURES combines 'RIFF' and 'WAVE' as b'RIFFWAVE'.

SIGNATURES = (
    Signature(
        Identity("WAVE", "RIFF", "Type [WAVE] derived from [RIFF]", "little"),
        b"\x52\x49\x46\x46\x57\x41\x56\x45",
        4,
    ),
    Signature(
        Identity("WAVE", "RF64", "Type [WAVE] derived from [RF64]", "little"),
        b"\x52\x46\x36\x34\x57\x41\x56\x45",
        4,
    ),
    Signature(
        Identity("WAVE", "BW64", "Type [WAVE] derived from [BW64]", "little"),
        b"\x42\x57\x36\x34\x57\x41\x56\x45",
        4,
    ),
    Signature(
        Identity("WAVE", "RIFX", "Type [WAVE] derived from [RIFX]", "big"),
        b"\x52\x49\x46\x58\x57\x41\x56\x45",
        4,
    ),
    Signature(
        Identity("WAVE", "FFIR", "Type [WAVE] derived from [FFIR]", "big"),
        b"\x46\x46\x49\x52\x57\x41\x56\x45",
        4,
    ),
)
