from dataclasses import dataclass
from typing import List

from ._types import FourCC, Size, Payload


@dataclass
class BaseChunk:
    """Common structure that all RIFF chunks adhere to."""

    identifier: FourCC
    size: Size


@dataclass
class GenericChunk(BaseChunk):
    """Default chunk for unsupported or unparsed chunks."""

    data: Payload


@dataclass
class SubFormat:
    audio_format: int
    guid: str


@dataclass
class PCMFormat(BaseChunk):
    """Standard ['fmt '] chunk."""

    audio_format: int
    num_channels: int
    sample_rate: int
    byte_rate: int
    block_align: int
    bits_per_sample: int

    # fixes mypy!
    extension_size: int
    valid_bits_per_sample: int
    channel_mask: int  # bitmask
    speaker_layout: List[str]
    sfmt: SubFormat
    version: int
    pvoc_size: int
    word_format: int
    analysis_format: int
    source_format: int
    window_type: int
    bin_count: int
    window_length: int
    overlap: int
    frame_align: int
    analysis_rate: float
    window_param: float


@dataclass
class ExtendedFormat(PCMFormat):
    """Extended ['fmt '] chunk."""

    extension_size: int


@dataclass
class ExtensibleFormat(ExtendedFormat):
    """Extensible ['fmt '] chunk."""

    valid_bits_per_sample: int
    channel_mask: int  # bitmask
    speaker_layout: List[str]
    sfmt: SubFormat


@dataclass
class PEXFormat(ExtensibleFormat):
    """PVOC-EX fields."""

    version: int
    pvoc_size: int
    word_format: int
    analysis_format: int
    source_format: int
    window_type: int
    bin_count: int
    window_length: int
    overlap: int
    frame_align: int
    analysis_rate: float
    window_param: float
