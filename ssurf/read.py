from typing import List, Protocol, Union

from ._types import Source, Stream
from .chunk import Chunk
from .chunk_models import (
    ExtendedFormat,
    ExtensibleFormat,
    PCMFormat,
    PEXFormat,
)
from .normalize import normalize_stream


class FormatReader(Protocol):
    """Protocol for reading and retrieving information from a WAVE stream."""

    # NOTE: Reader == PCMReader

    @property
    def audio_format(self) -> int:
        """Audio format of the stream."""

    @property
    def num_channels(self) -> int:
        """Number of channels in the stream."""

    @property
    def sample_rate(self) -> int:
        """Sample rate of the stream."""

    @property
    def byte_rate(self) -> int:
        """Byte rate of the stream."""

    @property
    def block_align(self) -> int:
        """Block alignment of the stream."""

    @property
    def bits_per_sample(self) -> int:
        """Bits per sample of the stream."""

    @property
    def bit_depth(self) -> int:
        """Same as bits per sample."""

    @property
    def encoding(self) -> str:
        """Audio encoding format."""


class PCMReader:
    """Reader for PCM (Pulse Code Modulation) audio format streams."""

    def __init__(self, format: PCMFormat):
        self.format = format

    @property
    def audio_format(self) -> int:
        return self.format.audio_format

    @property
    def num_channels(self) -> int:
        return self.format.num_channels

    @property
    def sample_rate(self) -> int:
        return self.format.sample_rate

    @property
    def byte_rate(self) -> int:
        return self.format.byte_rate

    @property
    def block_align(self) -> int:
        return self.format.block_align

    @property
    def bits_per_sample(self) -> int:
        return self.format.bits_per_sample

    @property
    def bit_depth(self) -> int:
        return self.format.bits_per_sample

    @property
    def encoding(self) -> str:
        return ""

    # return ENCODING_CODES.get(self.audio_format, None)


class ExtendedReader(PCMReader):
    """Reader for extended (non-PCM) audio stream formats."""

    def __init__(self, format: ExtendedFormat):
        super().__init__(format)
        self.format = format

    @property
    def extension_size(self) -> int:
        return self.format.extension_size


class ExtensibleReader(ExtendedReader):
    """Reader for extensible audio stream formats."""

    def __init__(self, format: ExtensibleFormat):
        super().__init__(format)
        self.format = format

    @property
    def valid_bits_per_sample(self) -> int:
        return self.format.valid_bits_per_sample

    @property
    def channel_mask(self) -> int:
        return self.format.channel_mask

    @property
    def speaker_layout(self) -> List[str]:
        return self.format.speaker_layout

    @property
    def audio_format(self) -> int:
        # Override with true audio_format stored in SubFormat
        return self.format.sfmt.audio_format

    @property
    def guid(self) -> str:
        return self.format.sfmt.guid

    @property
    def encoding(self) -> str:
        return ""

    # return ENCODING_CODES.get(self.audio_format, None)


class PEXReader(ExtensibleReader):
    """Custom reader for extensible PVOC-EX audio streams formats."""

    # NOTE: Implementation is not fully confirmed as correct.
    def __init__(self, format: PEXFormat):
        super().__init__(format)
        self.format = format

    @property
    def version(self) -> int:
        return self.format.version

    @property
    def pvoc_size(self) -> int:
        return self.format.pvoc_size

    @property
    def word_format(self) -> int:
        return self.format.word_format

    @property
    def analysis_format(self) -> int:
        return self.format.analysis_format

    @property
    def source_format(self) -> int:
        return self.format.source_format

    @property
    def window_type(self) -> int:
        return self.format.window_type

    @property
    def num_analysis_bins(self) -> int:
        return self.format.bin_count

    @property
    def bin_count(self) -> int:
        return self.format.bin_count

    @property
    def window_length(self) -> int:
        return self.format.window_length

    @property
    def overlap(self) -> int:
        return self.format.overlap

    @property
    def frame_align(self) -> int:
        return self.format.frame_align

    @property
    def analysis_rate(self) -> float:
        return self.format.analysis_rate

    @property
    def window_param(self) -> float:
        return self.format.window_param

    # ----- string representations & other values

    @property
    def word_format_str(self) -> str:
        if self.format.word_format == 0:
            return "IEEE_FLOAT"
        elif self.format.word_format == 1:
            return "IEEE_DOUBLE"
        else:
            return "UNKNOWN"

    @property
    def analysis_format_str(self) -> str:
        if self.format.analysis_format == 0:
            return "PVOC_AMP_FREQ"
        elif self.format.word_format == 1:
            return "PVOC_AMP_PHASE"
        else:
            return "UNKNOWN"

    @property
    def source_format_str(self) -> str:
        if self.format.source_format == 0:
            return "WAVE_FORMAT_PCM"
        elif self.format.source_format == 3:
            return "WAVE_FORMAT_IEEE_FLOAT"
        else:
            return "UNKNOWN"

    @property
    def window_type_str(self) -> str:
        if self.format.window_type == 0:
            return "PVOC_HAMMING"
        elif self.format.window_type == 1:
            return "PVOC_HANNING"
        elif self.format.window_type == 2:
            return "PVOC_KAISER"
        elif self.format.window_type == 3:
            return "PVOC_RECT"
        # Is PVOC_CUSTOM its own value?
        else:
            return "PVOC_CUSTOM"

    @property
    def beta(self) -> float:
        if self.window_type == 2:
            return self.window_param if self.window_param != 0 else 6.8
        else:
            raise ValueError(
                "[beta] is an associated parameter of the PVOC_KAISER window."
            )


class Read:
    """Read and retrieve information from a WAVE stream."""

    def __init__(self, source: Source):
        self._source = source

        self._chunks = self.initialize_chunks()
        self._parsed = self.initialize_parser()
        self._reader = self.initialize_reader()

    @property
    def stream(self) -> Stream:
        """Returns a normalized stream from the source."""
        return normalize_stream(self._source)

    @property
    def file_size(self) -> int:
        """Returns the size of the WAVE file in bytes."""
        return len(self.stream)

    def initialize_validator(self): ...

    # File signature detection

    def initialize_chunks(self):
        """Initializes chunks by reading from the source stream."""
        stream = self.stream
        chunk = Chunk(stream)
        chunks = {}
        # ignore = False

        for chunk_identifier, chunk_size, chunk_data in chunk.get_chunks():
            chunks[chunk_identifier] = (chunk_size, chunk_data)

        self._byteorder = chunk.byteorder
        self._master = chunk.master
        self._formtype = chunk.formtype
        self._ds64 = chunk.ds64
        self._chunk_identifiers = chunk.chunk_identifiers

        return chunks

    def initialize_parser(self): ...

    # Parse raw chunks

    def initialize_reader(self): ...

    # Set reader based on parser mode

    def initialize(self): ...

    # --- WAVE-specific accessible information

    @property
    def byteorder(self) -> str:
        """Returns the endianness of the stream."""
        return self._byteorder

    @property
    def chunk_list(self) -> list:
        """Returns a list of all chunk identifiers in the WAVE stream."""
        return self._chunk_identifiers

    @property
    def ds64(self) -> Union[dict, None]:
        """Returns the ds64 chunk."""
        return self._ds64

    @property
    def formtype(self) -> str:
        """Returns the RIFF formtype."""
        return self._formtype

    @property
    def is_extensible(self) -> bool:
        """Returns whether the WAVE file is an extensible format."""
        return isinstance(self._reader, ExtensibleReader)

    @property
    def master(self) -> str:
        """Returns the master RIFF identifier."""
        return self._master

    def all(self) -> dict:
        """Returns all parsed chunks from the stream."""
        return {}

    def all_raw(self) -> dict:
        """Returns all raw chunks from the stream."""
        return self._chunks

    def get_chunk(self, chunk_identifier: str) -> Union[tuple, None]:
        """Returns the parsed specified chunk."""
        return ()

    def get_chunk_raw(self, chunk_identifier: str) -> Union[tuple, None]:
        """Returns the unparsed specified chunk."""
        return self._chunks.get(chunk_identifier, None)

    def get_summary(self) -> dict:
        """Returns a summary of the WAVE format and data chunk."""
        # Include byte_count and frame_count?
        return {}

    def has_chunk(self, chunk_identifier: str) -> bool:
        """Returns whether the specified chunk exists in the WAVE stream."""
        return chunk_identifier in self._chunk_identifiers

    # def sanity(self) -> List[PerverseError]: ...
    # """Performs a sanity check on the WAVE stream."""

    def __getattr__(self, item):
        """Delegates access to the actual reader."""
        if self._reader is None:
            raise AttributeError("Reader not initialized.")
        # Delegate attribute access to the reader
        return getattr(self._reader, item)
