import io
import struct
import uuid
import xml.etree.ElementTree as ET

from typing import Generator, Tuple, Union

from ._constants import (
    CF_TYPES,
    CODING_HISTORY_LO,
    DEFAULT_ENCODING,
    EXTENSIBLE,
    FORMAT_CHUNK_LOCATION,
    GENERIC_CHANNEL_MASK_MAP,
    PVOC_EX,
    STRC_CHUNK_LOCATION,
    WAVE_FORMAT_EXTENDED,
    WAVE_FORMAT_EXTENSIBLE,
    WAVE_FORMAT_PCM,
    WAVE_FORMAT_PVOC_EX,
)
from ._errors import PerverseError
from ._types import Byteorder, Payload, Size
from .chunk_models import (
    # Sub chunk models
    AudioID,
    CuePoint,
    LabelNote,
    LabeledText,
    SampleLoop,
    SliceBlock,
    # Real chunk models
    AcidChunk,
    ADTLChunk,
    BroadcastChunk,
    CartChunk,
    ChnaChunk,
    CueChunk,
    DataChunk,
    DisplayChunk,
    FactChunk,
    InfoChunk,
    InstrumentChunk,
    MD5Chunk,
    PeakEnvelopeChunk,
    SampleChunk,
    StrcChunk,
    XMLChunk,
    # Format chunks
    SubFormat,
    PCMFormat,
    ExtendedFormat,
    ExtensibleFormat,
    PEXFormat,
)
from .utils import sanitize_fallback


class CKDecoder:
    def __init__(self, byteorder: Byteorder, sign: str):
        self._byteorder = byteorder
        self._sign = sign

        self._mode = None
        self._sanity = []

    @property
    def byteorder(self) -> Byteorder:
        return self._byteorder

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def sign(self) -> str:
        return self._sign

    @property
    def sanity(self) -> []:
        return self._sanity

    def decode_acid(self, payload: Payload) -> AcidChunk:
        """Decoder for the ['acid'] chunk."""
        default_pattern = f"{self.sign}IHHfIHHf"
        (
            properties,
            root_note,
            unknown_one,
            unknown_two,
            beat_count,
            meter_denominator,
            meter_numerator,
            tempo,
        ) = struct.unpack(default_pattern, payload[:24])

        is_oneshot = (properties & 0x01) != 0
        is_root_note = (properties & 0x02) != 0
        is_stretched = (properties & 0x04) != 0
        is_disk_based = (properties & 0x08) != 0
        is_unknown = (properties & 0x10) != 0

        return AcidChunk(
            properties=properties,
            is_oneshot=is_oneshot,
            is_loop=not is_oneshot,  # inverse of is_oneshot
            is_root_note=is_root_note,
            is_stretched=is_stretched,
            is_disk_based=is_disk_based,
            is_ram_based=not is_disk_based,
            is_unknown=is_unknown,
            root_note=root_note,
            unknown_one=unknown_one,
            unknown_two=unknown_two,
            beat_count=beat_count,
            meter_denominator=meter_denominator,
            meter_numerator=meter_numerator,
            tempo=tempo,
        )

    def decode_adtl(self, payload: Payload) -> ADTLChunk:
        """Decoder for the ['adtl'] chunk."""
        (sub_chunk_id, sub_chunk_size) = struct.unpack(f"{self.sign}4sI", payload[:8])

        sub_chunk_id = sanitize_fallback(sub_chunk_id, "ascii")

        if sub_chunk_id in ["labl", "note"]:
            (cue_point_id) = struct.unpack(f"{self.sign}I", payload[8:12])
            sub_data = sanitize_fallback(payload[16:], "ascii")

            return ADTLChunk(
                sub_chunk_id=sub_chunk_id,
                ascii_data=LabelNote(cue_point_id=cue_point_id, data=sub_data),
            )

        elif sub_chunk_id == "ltxt":
            (
                cue_point_id,
                sample_length,
                purpose_id,
                country,
                language,
                dialect,
                code_page,
            ) = struct.unpack(f"{self.sign}IIIHHHH", payload[8:28])

            sub_data = sanitize_fallback(payload[32:], "ascii")

            return ADTLChunk(
                sub_chunk_id=sub_chunk_id,
                ascii_data=LabeledText(
                    cue_point_id=cue_point_id,
                    sample_length=sample_length,
                    purpose_id=purpose_id,
                    country=country,
                    language=language,
                    dialect=dialect,
                    code_page=code_page,
                    data=sub_data,
                ),
            )

    def decode_bext(self, payload: Payload) -> BroadcastChunk:
        """Decoder for the ['bext'] chunk."""
        stream = io.BytesIO(payload)

        description, originator, originator_reference, origin_date, origin_time = (
            struct.unpack("256s32s32s10s8s", stream.read(338))
        )

        description = sanitize_fallback(description, "ascii")
        originator = sanitize_fallback(originator, "ascii")
        originator_reference = sanitize_fallback(originator_reference, "ascii")
        origin_date = sanitize_fallback(origin_date, "ascii")
        origin_time = sanitize_fallback(origin_time, "ascii")

        time_reference_low, time_reference_high, version = struct.unpack(
            "IIH", stream.read(10)
        )
        smpte_umid = sanitize_fallback(
            struct.unpack("63s", stream.read(63))[0], "ascii"
        )

        loudness_values = struct.unpack("5H", stream.read(10))
        (
            loudness_value,
            loudness_range,
            max_true_peak_level,
            max_momentary_loudness,
            max_short_term_loudness,
        ) = loudness_values

        coding_history = sanitize_fallback(payload[CODING_HISTORY_LO:], "ascii")

        return BroadcastChunk(
            description=description,
            originator=originator,
            originator_reference=originator_reference,
            origin_date=origin_date,
            origin_time=origin_time,
            time_reference_low=time_reference_low,
            time_reference_high=time_reference_high,
            version=version,
            smpte_umid=smpte_umid,
            loudness_value=loudness_value,
            loudness_range=loudness_range,
            max_true_peak_level=max_true_peak_level,
            max_momentary_loudness=max_momentary_loudness,
            max_short_term_loudness=max_short_term_loudness,
            coding_history=coding_history,
        )

    def decode_cart(self, payload: Payload, size: Size) -> CartChunk:
        """Decoder for the ['cart'] chunk."""
        default_pattern = f"{self.sign}4s64s64s64s64s64s64s64s10s8s10s8s64s64s64sI"
        unpacked_data = struct.unpack(
            default_pattern, payload[: struct.calcsize(default_pattern)]
        )

        offset = struct.calcsize(default_pattern)

        post_timers = []
        for _ in range(8):
            timer_usage_id = (
                payload[offset : offset + 4].decode(DEFAULT_ENCODING).strip("\x00")
            )
            offset += 4
            timer_value = int.from_bytes(payload[offset : offset + 4], "little")
            offset += 4

            post_timers.append((timer_usage_id, timer_value))

            # Skip reserved
            offset += 276

            url = sanitize_fallback(payload[offset : offset + 1024], DEFAULT_ENCODING)
            offset += 1024

            left_bytes = size - offset
            tag_text = (
                sanitize_fallback(
                    payload[offset : offset + left_bytes], DEFAULT_ENCODING
                )
                if left_bytes > 0
                else ""
            )

            # Sanitize and decode the previously unpacked data
            unpacked_values = [
                sanitize_fallback(value, DEFAULT_ENCODING)
                for value in unpacked_data[:15]
            ]

            return CartChunk(
                version=unpacked_values[0],
                title=unpacked_values[1],
                artist=unpacked_values[2],
                cut_id=unpacked_values[3],
                client_id=unpacked_values[4],
                category=unpacked_values[5],
                classification=unpacked_values[6],
                out_cue=unpacked_values[7],
                start_date=unpacked_values[8],
                start_time=unpacked_values[9],
                end_date=unpacked_values[10],
                end_time=unpacked_values[11],
                producer_app_id=unpacked_values[12],
                producer_app_version=unpacked_values[13],
                user_defined_text=unpacked_values[14],
                level_reference=unpacked_data[15],
                post_timers=post_timers,
                reserved=None,
                url=url,
                tag_text=tag_text,
            )

    def decode_chna(self, payload: Payload) -> ChnaChunk:
        """Decoder for the ['chna'] chunk."""
        default_pattern = f"{self.sign}HH"
        (track_count, uid_count) = struct.unpack(default_pattern, payload[:4])

        # Source: https://adm.ebu.io/reference/excursions/chna_chunk.html
        # struct audioID
        # {
        #   WORD    trackIndex;     // index of track in file
        #   CHAR    UID[12];        // audioTrackUID value
        #   CHAR    trackRef[14];   // audioTrackFormatID reference
        #   CHAR    packRef[11];    // audioPackFormatID reference
        #   CHAR    pad;            // padding byte to ensure even number of bytes
        # }
        track_pattern = f"{self.sign}H12s14s11sc"
        track_ids = []
        offset = 4

        for _ in range(uid_count):
            (track_index, uid, track_reference, pack_reference, pad) = struct.unpack(
                track_pattern, payload[offset : offset + 40]
            )

            uid = sanitize_fallback(uid, "ascii")
            track_reference = sanitize_fallback(track_reference, "ascii")
            pack_reference = sanitize_fallback(pack_reference, "ascii")
            padded = pad == b"\x00"

            audio_id = AudioID(
                track_index=track_index,
                uid=uid,
                track_reference=track_reference,
                pack_reference=pack_reference,
                padded=padded,
            )

            track_ids.append(audio_id)
            offset += 40

        return ChnaChunk(
            track_count=track_count,
            uid_count=uid_count,
            track_ids=track_ids,
        )

    def decode_cue(self, payload: Payload) -> CueChunk:
        """Decoder for the ['cue '] chunk."""
        point_count = struct.unpack(f"{self.sign}I", payload[:4])

        cue_points = []
        curr = 4

        for cue in range(point_count[0]):
            (point_id, position, chunk_id, chunk_start, block_start, sample_start) = (
                struct.unpack(f"{self.sign}IIIIII", payload[curr : curr + 24])
            )

            cue_point = CuePoint(
                point_id, position, chunk_id, chunk_start, block_start, sample_start
            )

            cue_points.append(cue_point)
            curr += 24

        return CueChunk(
            point_count=point_count[0],
            cue_points=cue_points,
        )

    def decode_data(self, payload: Payload, size: Size) -> DataChunk:
        """Decoder for the ['data'] chunk."""
        return DataChunk(byte_count=size, frame_count=None)

    def decode_disp(self, payload: Payload) -> DisplayChunk:
        """Decoder for the ['DISP'] chunk."""
        cftype_value = struct.unpack("I", payload[:4])[0]
        all_that_remains = sanitize_fallback(payload[4:], DEFAULT_ENCODING)
        cftype = CF_TYPES.get(cftype_value, "UNKNOWN_TYPE")

        return DisplayChunk(ftype=cftype, data=all_that_remains)

    def decode_fact(self, payload: Payload) -> FactChunk:
        """Decoder for the ['fact'] chunk."""
        samples = struct.unpack(f"{self.sign}I", payload[:4])
        return FactChunk(samples=samples[0])

    def decode_fmt(
        self, payload: Payload, size: Size
    ) -> Union[ExtendedFormat, ExtensibleFormat, PCMFormat, PEXFormat]:
        """Decoder for the ['fmt '] chunk."""

        default_pattern = f"{self.sign}HHIIHH"
        sanity = []
        (
            audio_format,
            channel_count,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
        ) = struct.unpack(default_pattern, payload[:16])

        # Determine the format type based on audio_format.
        # Non-PCM data MUST have an extended portion.

        extension_size = None
        valid_bits_per_sample = None
        channel_mask = None
        speaker_layout = None
        subformat = None

        version = None
        pvoc_size = None
        word_format = None
        analysis_format = None
        source_format = None
        window_type = None
        bin_count = None
        window_length = None
        overlap = None
        frame_align = None
        analysis_rate = None
        window_param = None

        mode = WAVE_FORMAT_PCM  # Default to PCM

        if audio_format != 1 and size == 16:
            location = f"{FORMAT_CHUNK_LOCATION} -- AUDIO FORMAT / SIZE"
            error_message = "NON-PCM FORMATS MUST CONTAIN AN EXTENSION FIELD."
            sanity.append(PerverseError(location, error_message))

            # ..zz: The 'Hard Hard_Vox.wav' file has IEEE float, but no extended field
            # Should a PerverseMode be created rather than setting it to None?

        elif audio_format == EXTENSIBLE:
            mode = WAVE_FORMAT_EXTENSIBLE

            extension_size, valid_bits_per_sample, cmask = struct.unpack(
                f"{self.sign}HHI", payload[16:24]
            )

            sfmt = payload[24:40]
            channel_mask = cmask

            speaker_layout = [
                GENERIC_CHANNEL_MASK_MAP.get(bit, "Unknown")
                for bit in GENERIC_CHANNEL_MASK_MAP
                if cmask & bit
            ]

            format_code = struct.unpack(f"{self.sign}H", sfmt[:2])[0]

            # TODO: is this correct for PVOC-EX?
            guid = uuid.UUID(bytes=sfmt[:16])
            subformat = SubFormat(audio_format=format_code, guid=str(guid))

            if str(guid) in PVOC_EX:
                if size != 80:
                    location = f"{FORMAT_CHUNK_LOCATION} -- PVOC-EX SIZE"
                    error_message = f"PVOC-EX FORMAT MUST ADHERE BE SIZE 80 NOT {size}."
                else:
                    mode = WAVE_FORMAT_PVOC_EX
                    (
                        version,
                        pvoc_size,
                    ) = struct.unpack(f"{self.sign}II", payload[40:48])

                    index = 48
                    (
                        word_format,
                        analysis_format,
                        source_format,
                        window_type,
                        bin_count,
                        window_length,
                        overlap,
                        frame_align,
                        analysis_rate,
                        window_param,
                    ) = struct.unpack(
                        f"{self.sign}HHHHIIIIff", payload[index : index + pvoc_size]
                    )

            else:
                if size != 40:
                    location = f"{FORMAT_CHUNK_LOCATION} -- AUDIO FORMAT / SIZE"
                    error_message = f"AUDIO FORMAT (EXTENSIBLE / 65534 / 0xFFFE) MUST BE SIZE 40 NOT {size}"
                    sanity.append(PerverseError(location, error_message))

        elif size == 18:
            mode = WAVE_FORMAT_EXTENDED

            extension_size = struct.unpack(f"{self.sign}H", payload[16:18])[0]

        else:
            if size != 16:
                location = f"{FORMAT_CHUNK_LOCATION} -- AUDIO FORMAT / SIZE"
                error_message = (
                    f"AUDIO FORMAT (PCM / 1 / 0x0001) MUST BE SIZE 16 NOT {size}."
                )
                sanity.append(PerverseError(location, error_message))

            mode = WAVE_FORMAT_PCM

        bitrate = byte_rate * 8
        bitrate_long = f"{bitrate / 1000} kb/s"

        self._sanity.append(sanity)
        self._mode = mode

        match mode:
            case "WAVE_FORMAT_PCM":
                return PCMFormat(
                    audio_format=audio_format,
                    num_channels=channel_count,
                    sample_rate=sample_rate,
                    byte_rate=byte_rate,
                    block_align=block_align,
                    bits_per_sample=bits_per_sample,
                    bitrate=bitrate,
                    bitrate_long=bitrate_long,
                )
            case "WAVE_FORMAT_EXTENDED":
                return ExtendedFormat(
                    audio_format=audio_format,
                    num_channels=channel_count,
                    sample_rate=sample_rate,
                    byte_rate=byte_rate,
                    block_align=block_align,
                    bits_per_sample=bits_per_sample,
                    bitrate=bitrate,
                    bitrate_long=bitrate_long,
                    extension_size=extension_size,
                )
            case "WAVE_FORMAT_EXTENSIBLE":
                return ExtensibleFormat(
                    audio_format=audio_format,
                    num_channels=channel_count,
                    sample_rate=sample_rate,
                    byte_rate=byte_rate,
                    block_align=block_align,
                    bits_per_sample=bits_per_sample,
                    bitrate=bitrate,
                    bitrate_long=bitrate_long,
                    extension_size=extension_size,
                    valid_bits_per_sample=valid_bits_per_sample,
                    channel_mask=channel_mask,
                    speaker_layout=speaker_layout,
                    sfmt=subformat,
                )
            case "WAVE_FORMAT_PVOC_EX":
                return PEXFormat(
                    audio_format=audio_format,
                    num_channels=channel_count,
                    sample_rate=sample_rate,
                    byte_rate=byte_rate,
                    block_align=block_align,
                    bits_per_sample=bits_per_sample,
                    bitrate=bitrate,
                    bitrate_long=bitrate_long,
                    extension_size=extension_size,
                    valid_bits_per_sample=valid_bits_per_sample,
                    channel_mask=channel_mask,
                    speaker_layout=speaker_layout,
                    sfmt=subformat,
                    version=version,
                    pvoc_size=pvoc_size,
                    word_format=word_format,
                    analysis_format=analysis_format,
                    source_format=source_format,
                    window_type=window_type,
                    bin_count=bin_count,
                    window_length=window_length,
                    overlap=overlap,
                    frame_align=frame_align,
                    analysis_rate=analysis_rate,
                    window_param=window_param,
                )

    def decode_info(self, payload: Payload) -> InfoChunk:
        """Decoder for the ['INFO'] chunk."""
        info_chunk = InfoChunk()

        def yield_info() -> Generator[Tuple[str | bytes, int, str | bytes], None, None]:
            """Decodes the provided ['INFO' / INFO] chunk data."""
            stream = io.BytesIO(payload)
            while True:
                id_bytes = stream.read(4)
                if len(id_bytes) < 4:
                    break

                tag_identifier = sanitize_fallback(id_bytes, "ascii")
                size_bytes = stream.read(4)
                if len(size_bytes) < 4:
                    break

                tag_size = int.from_bytes(size_bytes, self.byteorder)
                if tag_size % 2 != 0:
                    tag_size += 1

                data_bytes = stream.read(tag_size)
                tag_data = sanitize_fallback(data_bytes, "ascii")
                if not tag_data:
                    tag_data = sanitize_fallback(data_bytes, DEFAULT_ENCODING)

                yield (tag_identifier, tag_size, tag_data)

        for tag_identifier, _, tag_data in yield_info():
            match tag_identifier:
                case "IARL":
                    info_chunk.archival_location = tag_data
                case "IART":
                    info_chunk.artist = tag_data
                case "ICMS":
                    info_chunk.commissioned = tag_data
                case "ICMT":
                    info_chunk.comment = tag_data
                case "ICOP":
                    info_chunk.copyright = tag_data
                case "ICRD":
                    info_chunk.creation_date = tag_data
                case "ICRP":
                    info_chunk.cropped = tag_data
                case "IDIM":
                    info_chunk.dimensions = tag_data
                case "IDPI":
                    info_chunk.dots_per_inch = tag_data
                case "IENG":
                    info_chunk.engineer = tag_data
                case "IGNR":
                    info_chunk.genre = tag_data
                case "IKEY":
                    info_chunk.keywords = tag_data
                case "ILGT":
                    info_chunk.lightness = tag_data
                case "IMED":
                    info_chunk.medium = tag_data
                case "INAM":
                    info_chunk.title = tag_data
                case "IPLT":
                    info_chunk.palette = tag_data
                case "IPRD":
                    info_chunk.product = tag_data
                    info_chunk.album = tag_data
                case "ISBJ":
                    info_chunk.subject = tag_data
                case "ISFT":
                    info_chunk.software = tag_data
                case "ISRC":
                    info_chunk.source = tag_data
                case "ISRF":
                    info_chunk.source_form = tag_data
                case "ITCH":
                    info_chunk.technician = tag_data

        return info_chunk

    def decode_inst(self, payload: Payload) -> InstrumentChunk:
        """Decoder for the ['inst'] chunk."""
        default_pattern = f"{self.sign}BBBBBBB"
        (
            unshifted_note,
            fine_tuning,
            gain,
            low_note,
            high_note,
            low_velocity,
            high_velocity,
        ) = struct.unpack(default_pattern, payload[:7])

        return InstrumentChunk(
            unshifted_note=unshifted_note,
            fine_tuning=fine_tuning,
            gain=gain,
            low_note=low_note,
            high_note=high_note,
            low_velocity=low_velocity,
            high_velocity=high_velocity,
        )

    def decode_levl(self, payload: Payload) -> PeakEnvelopeChunk:
        """Decoder for the ['levl'] chunk."""
        default_pattern = "<IIIIIIII"
        # Must be little-endian
        (
            version,
            format,
            points_per_value,
            block_size,
            channel_count,
            frame_count,
            position,
            offset,
        ) = struct.unpack(default_pattern, payload[:32])

        # The timestamp and reserved spaces are always 28 bytes and 60 bytes respectively
        timestamp = sanitize_fallback(payload[32:60], "unicode-escape")
        reserved = sanitize_fallback(payload[60:120], DEFAULT_ENCODING)

        # Everything after reserved is the peak envelope data
        peak_envelope_data = payload[120:]

        return PeakEnvelopeChunk(
            version=version,
            format=format,
            points_per_value=points_per_value,
            block_size=block_size,
            channel_count=channel_count,
            frame_count=frame_count,
            position=position,
            offset=offset,
            timestamp=timestamp[:-2],
            reserved=reserved,
            peak_envelope_data=peak_envelope_data,
        )

    def decode_md5(self, payload: Payload) -> MD5Chunk:
        """Decoder for the ['MD5 '] chunk."""
        checksum = int.from_bytes(payload[:16], byteorder=self.byteorder)
        return MD5Chunk(checksum=checksum)

    def decode_smpl(self, payload: Payload) -> SampleChunk:
        """Decoder for the ['smpl'] chunk."""
        default_pattern = f"{self.sign}iiiiiiiii"

        (
            manufacturer,
            product,
            sample_period,
            unity_note,
            pitch_fraction,
            smpte_format,
            smpte_offset,
            sample_loop_count,
            sampler_data_size,
        ) = struct.unpack(default_pattern, payload[:36])

        hours = (smpte_offset >> 24) & 0xFF
        minutes = (smpte_offset >> 16) & 0xFF
        seconds = (smpte_offset >> 8) & 0xFF
        frames = smpte_offset & 0xFF
        true_smpte_offset = (
            f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}/{smpte_format}"
        )

        loop_pattern = f"{self.sign}IIIIII"
        sample_loops = []
        offset = 36
        for _ in range(sample_loop_count):
            (identifier, loop_type, start, end, fraction, loop_count) = struct.unpack(
                loop_pattern, payload[offset : offset + 24]
            )

            sample_loop = SampleLoop(
                identifier=identifier,
                loop_type=loop_type,
                start=start,
                end=end,
                fraction=fraction,
                loop_count=loop_count,
            )

            sample_loops.append(sample_loop)
            offset += 24

        sampler_data = (
            payload[offset : offset + sampler_data_size]
            if sampler_data_size > 0
            else None
        )

        # TODO: perform sanity checks
        # Everything seems to be correct, but the smpte_offset needs to be verified
        # with test files that don't have all bits set to 0
        # Also, should sample loop identifier output (131072) vs. (0x200) vs. (0020)
        # self._sanity.append(sanity)

        return SampleChunk(
            manufacturer=manufacturer,
            product=product,
            sample_period=sample_period,
            unity_note=unity_note,
            pitch_fraction=pitch_fraction,
            smpte_format=smpte_format,
            smpte_offset=true_smpte_offset,
            sample_loop_count=sample_loop_count,
            sampler_data_size=sampler_data_size,
            sample_loops=sample_loops,
            sampler_data=sampler_data,
        )

    def decode_strc(self, payload: Payload) -> StrcChunk:
        """Decoder for the ['strc'] chunk,"""
        header_pattern = f"{self.sign}IIIIIII"
        sanity = []
        (
            unknown1,
            slice_count,
            unknown2,
            unknown3,
            unknown4,
            unknown5,
            unknown6,
        ) = struct.unpack(header_pattern, payload[:28])

        slice_pattern = f"{self.sign}IIQQII"
        slice_blocks = []
        offset = 28
        total_data_size = len(payload)

        for i in range(slice_count):
            if offset + 32 > total_data_size:
                location = f"{STRC_CHUNK_LOCATION} -- SLICE {i}"
                error_message = (
                    "NOT ENOUGH DATA TO UNPACK SLICE -- MISSING OR PADDED SLICE."
                )
                sanity.append(PerverseError(location, error_message))
                break

            try:
                (data1, data2, sample_position, sample_position2, data3, data4) = (
                    struct.unpack(slice_pattern, payload[offset : offset + 32])
                )
            except struct.error as e:
                location = f"{STRC_CHUNK_LOCATION} -- SLICE {i}"
                error_message = "SLICE {i} COULD NOT BE UNPACKED: {e}"
                sanity.append(PerverseError(location, error_message))
                break

            slice_block = SliceBlock(
                data1=data1,
                data2=data2,
                sample_position=sample_position,
                sample_position2=sample_position2,
                data3=data3,
                data4=data4,
            )
            slice_blocks.append(slice_block)
            offset += 32

        if len(slice_blocks) != slice_count:
            location = f"{STRC_CHUNK_LOCATION} -- SLICE BLOCKS"
            error_message = f"EXPECTED {slice_count} SLICES -- GOT {len(slice_blocks)}."
            sanity.append(PerverseError(location, error_message))

        self._sanity.append(sanity)

        return StrcChunk(
            unknown1=unknown1,
            slice_count=slice_count,
            unknown2=unknown2,
            unknown3=unknown3,
            unknown4=unknown4,
            unknown5=unknown5,
            unknown6=unknown6,
            slice_blocks=slice_blocks,
        )

    def decode_xml(self, payload: Payload) -> XMLChunk:
        """Decoder for the ['aXML'] | ['iXML'] | ['_PMX'] chunk."""
        dummy = sanitize_fallback(payload, "utf-8")
        root = ET.fromstring(dummy)
        xml = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
        xml = xml.replace("encoding='utf8'", "encoding='UTF-8'")

        return XMLChunk(xml=xml)
