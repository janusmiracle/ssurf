from ._constants import DEFAULT_ENCODING

# from ._errors import PerverseError
from ._types import Byteorder
from .chunk_decoders import CKDecoder
from .chunk_models import GenericChunk
from .utils import byteorder_symbol

# Source: https://tech.ebu.ch/docs/tech/tech3285s3.pdf
# TODO: fix the names for everything (e.g. position = audio_sample_frame_index?)
# The decoding seems to work(?)
UNKNOWN_POSITIONS = "0xffffffff"  # -1 -- 0xFFFFFFFF

# Supported chunk identifiers
ACID_IDENTIFIER = "acid"
ADTL_IDENTIFIER = "adtl"
AXML_IDENTIFIER = "aXML"
BEXT_IDENTIFIER = "bext"
CART_IDENTIFIER = "cart"
CHNA_IDENTIFIER = "chna"
CUE_IDENTIFIER = "cue "
DATA_IDENTIFIER = "data"
DISP_IDENTIFIER = "DISP"
FACT_IDENTIFIER = "fact"
FMT_IDENTIFIER = "fmt "
INFO_IDENTIFIER = "INFO"
INST_IDENTIFIER = "inst"
IXML_IDENTIFIER = "iXML"
LEVL_IDENTIFIER = "levl"
LIST_IDENTIFIER = "LIST"
MD5_IDENTIFIER = "MD5 "
PMX_IDENTIFIER = "_PMX"
SMPL_IDENTIFIER = "smpl"
STRC_IDENTIFIER = "strc"

LIST_TYPES = [ADTL_IDENTIFIER, INFO_IDENTIFIER]


class Parse:
    def __init__(self, chunks: dict, byteorder: Byteorder):
        self._chunks = chunks
        self._byteorder = byteorder

        self._mode = None
        self._sanity = []

    @property
    def chunks(self) -> dict:
        return self._chunks

    @property
    def byteorder(self) -> Byteorder:
        return self._byteorder

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def sanity(self) -> []:
        return self._sanity

    def deparse(self):
        true_chunks = {}

        sign = byteorder_symbol(self.byteorder)

        # Initialize chunk decoders
        ckdec = CKDecoder(self.byteorder, sign)
        for identifier, size, payload in self.chunks:
            if identifier == LIST_IDENTIFIER:
                # Determine the list-type and overwrite
                identifier = payload[:4].decode(DEFAULT_ENCODING).strip()
                size -= 12
                payload = payload[4:]

            # Decode each payload
            match identifier:
                case "acid":
                    true_chunks[ACID_IDENTIFIER] = ckdec.decode_acid(payload)

                case "aXML" | "iXML" | "_PMX":
                    true_chunks[identifier] = ckdec.decode_xml(payload)

                case "bext":
                    true_chunks[BEXT_IDENTIFIER] = ckdec.decode_bext(payload)

                case "cart":
                    true_chunks[CART_IDENTIFIER] = ckdec.decode_cart(payload, size)

                case "chna":
                    true_chunks[CHNA_IDENTIFIER] = ckdec.decode_chna(payload)

                case "cue ":
                    true_chunks[CUE_IDENTIFIER] = ckdec.decode_cue(payload)

                case "data":
                    true_chunks[DATA_IDENTIFIER] = ckdec.decode_data(payload, size)

                case "DISP":
                    true_chunks[DISP_IDENTIFIER] = ckdec.decode_disp(payload)

                case "fact":
                    true_chunks[FACT_IDENTIFIER] = ckdec.decode_fact(payload)

                case "fmt ":
                    true_chunks[FMT_IDENTIFIER] = ckdec.decode_fmt(payload, size)

                case "INFO":
                    true_chunks[INFO_IDENTIFIER] = ckdec.decode_info(payload)

                case "inst":
                    true_chunks[INST_IDENTIFIER] = ckdec.decode_inst(payload)

                case "levl":
                    true_chunks[LEVL_IDENTIFIER] = ckdec.decode_levl(payload)

                case "MD5 ":
                    true_chunks[MD5_IDENTIFIER] = ckdec.decode_md5(payload)

                case "smpl":
                    true_chunks[SMPL_IDENTIFIER] = ckdec.decode_smpl(payload)

                case "strc":
                    true_chunks[STRC_IDENTIFIER] = ckdec.decode_strc(payload)

                case _:
                    true_chunks[identifier] = GenericChunk(payload=payload)

            true_chunks[identifier].identifier = identifier
            true_chunks[identifier].size = size

        if true_chunks["fmt "] and true_chunks["data"]:
            true_chunks["data"].frame_count = int(
                true_chunks["data"].byte_count / true_chunks["fmt "].block_align
            )

        self._mode = ckdec.mode
        self._sanity = ckdec.sanity

        return true_chunks
