from typing import Dict, Union

from ._types import Byteorder
from .signatures import SIGNATURES


def byteorder_symbol(byteorder: Byteorder) -> str:
    """Returns the corresponding byteorder symbol for stuct."""
    match byteorder:
        case "big":
            return ">"
        case "little":
            return "<"
        case _:
            raise ValueError("Invalid byteorder. Use 'big' or 'little'.")


def purge(base: Dict) -> Dict:
    """Removes None, empty strings, and empty list values from a given dictionary."""
    for key, value in list(base.items()):
        if value is None or value == "" or value == [] or value == b"":
            del base[key]
        elif isinstance(value, dict):
            base[key] = purge(value)

    return base


def sanitize_fallback(to_decode: bytes, encoding: str) -> Union[str, bytes]:
    """
    Decodes the provided bytes to the specified encoding, and sanitizes it of null bytes.

    Rather than ignoring any errors, it returns the input bytes.
    """
    try:
        return (
            to_decode.decode(encoding)
            .rstrip("\x00")
            .strip("\u0000")
            .replace("\x00", "")
        )
    except (UnicodeDecodeError, AttributeError):
        return to_decode


def search_signature(container: str) -> bool:
    """Searches SIGNATURES to see if target container exists."""
    return any(signature.identity.container == container for signature in SIGNATURES)
