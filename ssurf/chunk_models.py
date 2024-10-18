from dataclasses import dataclass, field
from typing import List, Optional, Union

from ._types import FourCC, Size, Payload


@dataclass
class BaseChunk:
    """Common structure that all RIFF chunks adhere to."""

    identifier: Optional[FourCC] = field(default=None, init=False)
    size: Optional[Size] = field(default=None, init=False)


@dataclass
class GenericChunk(BaseChunk):
    """Default chunk for unsupported or unparsed chunks."""

    payload: Payload


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
    bitrate: int
    bitrate_long: str

    extension_size: Optional[int] = None
    valid_bits_per_sample: Optional[int] = None
    channel_mask: Optional[int] = None  # bitmask
    speaker_layout: Optional[List[str]] = None
    sfmt: Optional[SubFormat] = None
    version: Optional[int] = None
    pvoc_size: Optional[int] = None
    word_format: Optional[int] = None
    analysis_format: Optional[int] = None
    source_format: Optional[int] = None
    window_type: Optional[int] = None
    bin_count: Optional[int] = None
    window_length: Optional[int] = None
    overlap: Optional[int] = None
    frame_align: Optional[int] = None
    analysis_rate: Optional[float] = None
    window_param: Optional[float] = None


@dataclass
class ExtendedFormat(PCMFormat):
    """Extended ['fmt '] chunk."""

    extension_size: Optional[int] = None  # This can be overridden in PEXFormat


@dataclass
class ExtensibleFormat(ExtendedFormat):
    """Extensible ['fmt '] chunk."""

    valid_bits_per_sample: Optional[int] = None
    channel_mask: Optional[int] = None  # bitmask
    speaker_layout: Optional[List[str]] = None
    sfmt: Optional[SubFormat] = None


@dataclass
class PEXFormat(ExtensibleFormat):
    """PVOC-EX fields."""

    version: Optional[int] = None
    pvoc_size: Optional[int] = None
    word_format: Optional[int] = None
    analysis_format: Optional[int] = None
    source_format: Optional[int] = None
    window_type: Optional[int] = None
    bin_count: Optional[int] = None
    window_length: Optional[int] = None
    overlap: Optional[int] = None
    frame_align: Optional[int] = None
    analysis_rate: Optional[float] = None
    window_param: Optional[float] = None


@dataclass
class DataChunk(BaseChunk):

    byte_count: int
    frame_count: int


@dataclass
class FactChunk(BaseChunk):
    samples: int


@dataclass
class InfoChunk(BaseChunk):
    # fmt: off
    archival_location: Optional[str] = None     # -- IARL [ARCHIVAL LOCATION]
    artist: Optional[str] = None                # -- IART [ARTIST]
    commissioned: Optional[str] = None          # -- ICMS [COMMISIONED/CLIENT]
    comment: Optional[str] = None               # -- ICMT [COMMENT]
    copyright: Optional[str] = None             # -- ICOP [COPYRIGHT]
    creation_date: Optional[str] = None         # -- ICRD [CREATION DATE]
    cropped: Optional[str] = None               # -- ICRP [CROPPED]
    dimensions: Optional[str] = None            # -- IDIM [DIMENSIONS]
    dots_per_inch: Optional[str] = None         # -- IDPI [DPI SETTINGS]
    engineer: Optional[str] = None              # -- IENG [ENGINEER]
    genre: Optional[str] = None                 # -- IGNR [GENRE]
    keywords: Optional[str] = None              # -- IKEY [KEYWORDS]
    lightness: Optional[str] = None             # -- ILGT [LIGHTNESS SETTINGS]
    medium: Optional[str] = None                # -- IMED [MEDIUM]
    title: Optional[str] = None                 # -- INAM [TITLE]
    palette: Optional[str] = None               # -- IPLT [PALETTE]
    product: Optional[str] = None               # -- IPRD [PRODUCT]
    album: Optional[str] = None                 # Online taggers treat IPRD as an [ALBUM] field
    subject: Optional[str] = None               # -- ISBJ [SUBJECT]
    software: Optional[str] = None              # -- ISFT [SOFTWARE NAME]
    source: Optional[str] = None                # -- ISRC [SOURCE]
    source_form: Optional[str] = None           # -- ISRF [SOURCE FORM]
    technician: Optional[str] = None            # -- ITCH [TECHNICIAN]
    # fmt: on


@dataclass
class InstrumentChunk(BaseChunk):
    # fmt: off
    unshifted_note: int         # 0 - 127
    fine_tuning: int            # -50 - 50 in cents
    gain: int                   # volume setting in decibels
    low_note: int               # 0 - 127
    high_note: int              # 0 - 127
    low_velocity: int           # 0 - 127
    high_velocity: int          # 0 - 127
    # fmt: on


@dataclass
class PeakEnvelopeChunk(BaseChunk):
    # fmt: off
    version: str                # int?
    format: int                 # 1 or 2
    points_per_value: int       # 1 or 2
    block_size: int             # Default: 256
    channel_count: int
    frame_count: int
    # audio_frame_count: int    # block_size * peak_channel_count * peak_frame_count
    position: int
    offset: int
    timestamp: str              # size 28 -- YYYY:MM:DD:hh:mm:ss:uuu -- 2000:08:24:13:55:40:967
    reserved: str
    peak_envelope_data: bytes


@dataclass
class SampleLoop:
    identifier: str
    loop_type: int
    start: int
    end: int
    fraction: int
    loop_count: int


@dataclass
class SampleChunk(BaseChunk):
    # fmt: off
    manufacturer: str           # https://www.recordingblogs.com/wiki/midi-system-exclusive-message
    product: int
    sample_period: int          # in nanoseconds
    unity_note: int             # midi_unity_note -- between 0 and 127
    pitch_fraction: int         # midi_pitch_fraction
    smpte_format: int           # possible values: 0, 24, 25, 29, 30
    smpte_offset: str           # TODO: I should probably return the raw bits too?
    sample_loop_count: int
    sampler_data_size: int
    sample_loops: List[SampleLoop]
    sampler_data: Optional[bytes]
    # fmt: on


# NOTE: This implementation is based on `wav_read_acid_chunk` from libsndfile's wav.c.
#       The provided explanation MAY be incomplete and MAY not have been confirmed.


@dataclass
class AcidChunk(BaseChunk):
    properties: str
    # Based on the properties bitmask
    is_oneshot: bool
    is_loop: bool
    is_root_note: bool
    is_stretched: bool
    is_disk_based: bool
    is_ram_based: bool
    is_unknown: bool

    root_note: int
    unknown_one: int
    unknown_two: float
    beat_count: int

    # NOTE: Order could be incorrect here
    meter_denominator: int
    meter_numerator: int

    tempo: float


@dataclass
class CartChunk(BaseChunk):
    version: str = ""
    title: str = ""
    artist: str = ""
    cut_id: str = ""
    client_id: str = ""
    category: str = ""
    classification: str = ""
    out_cue: str = ""
    start_date: str = ""
    start_time: str = ""
    end_date: str = ""
    end_time: str = ""
    producer_app_id: str = ""
    producer_app_version: str = ""
    user_defined_text: str = ""
    level_reference: int = 0
    post_timers: list = None  # Initialize to None
    reserved: str = None  # Reserved can be None
    url: str = ""
    tag_text: str = ""

    def __post_init__(self):
        if self.post_timers is None:
            self.post_timers = []


@dataclass
class AudioID:
    track_index: int
    uid: str
    track_reference: str
    pack_reference: str
    padded: bool


@dataclass
class ChnaChunk(BaseChunk):
    track_count: int
    uid_count: int
    track_ids: List[AudioID]


# This chunk is completely undocumented and related to ACID.
# Source: http://forum.cakewalk.com/Is-the-ACIDized-WAV-format-documented-m43324.aspx

# The implementation might not be accurate due to lack of documentation.
# Any insights or corrections are welcome.
# No testing will be created for this chunk.


@dataclass
class SliceBlock:
    data1: int
    data2: int
    sample_position: int
    sample_position2: int
    data3: int
    data4: int


@dataclass
class StrcChunk(BaseChunk):

    unknown1: int
    slice_count: int
    unknown2: int
    unknown3: int
    unknown4: int
    unknown5: int
    unknown6: int
    slice_blocks: List[SliceBlock]


@dataclass
class BroadcastChunk(BaseChunk):

    # fmt: off
    description: str                    # ASCII 256
    originator: str                     # ASCII 32
    originator_reference: str           # ASCII 32
    origin_date: str                    # ASCII 10 --YYYY:MM:DD
    origin_time: str                    # ASCII 8 --HH:MM:SS
    time_reference_low: int
    time_reference_high: int
    version: int                        # 2
    smpte_umid: str                     # 63
    loudness_value: int                 # 2
    loudness_range: int                 # 2
    max_true_peak_level: int            # 2
    max_momentary_loudness: int         # 2
    max_short_term_loudness: int        # 2
    coding_history: str
    # fmt: on


@dataclass
class DisplayChunk(BaseChunk):
    cftype: int
    data: str


@dataclass
class CuePoint:
    point_id: str
    position: int
    chunk_id: str
    chunk_start: int
    block_start: int
    sample_start: int


@dataclass
class CueChunk(BaseChunk):
    point_count: int
    cue_points: List[CuePoint]


@dataclass
class LabelNote:
    cue_point_id: str
    data: str


@dataclass
class LabeledText:
    cue_point_id: str
    sample_length: int
    purpose_id: str
    country: str
    language: str
    dialect: str
    code_page: str
    data: str


@dataclass
class ADTLChunk(BaseChunk):

    sub_chunk_id: str
    ascii_data: Union[LabelNote, LabeledText]


@dataclass
class XMLChunk(BaseChunk):
    xml: str


@dataclass
class MD5Chunk(BaseChunk):
    checksum: int
