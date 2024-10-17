from typing import Generator, List, Optional, Tuple

from ._constants import ENCODING, FALSE_SIZE, NULL_IDENTIFIER
from ._types import Byteorder, Stream

# Default chunks to ignore
IGNORE_CHUNKS = ["data", "JUNK", "FLLR", "PAD "]

# Only valid 'master' identifiers
RIFF_BASED = ["RIFF", "RIFX", "FIRR", "BW64"]


class Chunk:
    def __init__(
        self,
        stream: Stream,
        ignore_chunks: List[str] = IGNORE_CHUNKS,
    ):
        self._stream = stream
        self._ignore_chunks = ignore_chunks

        self.byteorder: Byteorder
        self.chunk_identifiers: List[str] = []

        self.master: Optional[str] = None
        self.formtype: Optional[str] = None
        self.ds64: Optional[dict] = None

    @property
    def stream(self) -> Stream:
        return self._stream

    @property
    def ignore_chunks(self) -> List[str]:
        return self._ignore_chunks

    def get_byteorder(self, master: str) -> Byteorder:
        """Determines the byte order based on the master chunk identifier."""
        if master in ["RIFF", "BW64", "RF64"]:
            return "little"
        elif master in ["RIFX", "FIRR"]:
            return "big"
        else:
            raise ValueError(f"Invalid master chunk identifier: {master}")

    def riff_based(self, master: str) -> bool:
        return master in RIFF_BASED

    def get_chunks(self) -> Generator[Tuple[str, int, bytes], None, None]:
        self.stream.seek(0)
        master = self.stream.read(4).decode(ENCODING)
        self.master = master

        self.byteorder = self.get_byteorder(master)

        master_size_bytes = self.stream.read(4)
        master_size = hex(int.from_bytes(master_size_bytes, byteorder=self.byteorder))

        formtype = self.stream.read(4).decode(ENCODING)
        self.formtype = formtype

        if master_size == FALSE_SIZE:
            # Size is set to -1, true size is stored in ds64
            yield from self._rf64()
        elif self.riff_based(master):
            yield from self._riff()
        else:
            raise ValueError(f"Unknown or unsupported format: {master}")

    def _riff(self) -> Generator[Tuple[str, int, bytes], None, None]:
        while True:
            identifier_bytes = self.stream.read(4)
            if len(identifier_bytes) < 4:
                break

            chunk_identifier = identifier_bytes.decode(ENCODING)
            # if chunk_identifier == "afsp":
            # records from the `afsp` chunk are transferred to DISP/LIST[INFO] chunks
            # thus, the `afsp` is ignored as it contains no size field
            # TODO: maybe don't skip this, file could contain afsp but no DISP/INFO
            # self._skip_afsp()
            # continue

            size_bytes = self.stream.read(4)
            if len(size_bytes) < 4:
                break

            chunk_size = int.from_bytes(size_bytes, byteorder=self.byteorder)
            # account for padding or null bytes if chunk_size is odd
            # NOTE: It seems that the `bext` chunk does not follow the
            # "All chunks MUST have an even size" rule, so it is ignored
            if chunk_size % 2 != 0 and chunk_identifier != "bext":
                chunk_size += 1

            # ignore certain chunks
            if self.ignore_chunks and chunk_identifier in self.ignore_chunks:
                chunk_data = b""
            else:
                chunk_data = self.stream.read(chunk_size)

            self.chunk_identifiers.append(chunk_identifier)
            yield (chunk_identifier, chunk_size, chunk_data)

            # Skip to the start of the next chunk
            self.stream.seek(chunk_size - len(chunk_data), 1)

    def _rf64(self) -> Generator[Tuple[str, int, bytes], None, None]:
        ds64_identifier = self.stream.read(4).decode(ENCODING)
        if ds64_identifier != "ds64":
            raise ValueError(f"Expected ds64 chunk but found {ds64_identifier}")

        # TODO: simplify this with struct
        ds64_size_bytes = self.stream.read(4)
        ds64_size = int.from_bytes(ds64_size_bytes, byteorder=self.byteorder)

        riff_low_size_bytes = self.stream.read(4)
        riff_low_size = int.from_bytes(riff_low_size_bytes, byteorder=self.byteorder)

        riff_high_size_bytes = self.stream.read(4)
        riff_high_size = int.from_bytes(riff_high_size_bytes, byteorder=self.byteorder)

        data_low_size_bytes = self.stream.read(4)
        data_low_size = int.from_bytes(data_low_size_bytes, byteorder=self.byteorder)

        data_high_size_bytes = self.stream.read(4)
        data_high_size = int.from_bytes(data_high_size_bytes, byteorder=self.byteorder)

        sample_low_count_bytes = self.stream.read(4)
        sample_low_count = int.from_bytes(
            sample_low_count_bytes, byteorder=self.byteorder
        )

        sample_high_count_bytes = self.stream.read(4)
        sample_high_count = int.from_bytes(
            sample_high_count_bytes, byteorder=self.byteorder
        )

        table_entry_count_bytes = self.stream.read(4)
        table_entry_count = int.from_bytes(
            table_entry_count_bytes, byteorder=self.byteorder
        )

        # Not accounting for table_entry_count > 0
        # Once a test file is procured, it will be done.

        self.ds64 = {
            "chunk_identifier": ds64_identifier,
            "chunk_size": ds64_size,
            "riff_low_size": riff_low_size,
            "riff_high_size": riff_high_size,
            "data_low_size": data_low_size,
            "data_high_size": data_high_size,
            "sample_low_count": sample_low_count,
            "sample_high_count": sample_high_count,
            "table_entry_count": table_entry_count,
        }

        # Skip to end of ds64 chunk
        current_location = self.stream.tell()
        self.stream.seek(current_location + table_entry_count * 12)

        while True:
            identifier_bytes = self.stream.read(4)
            if len(identifier_bytes) < 4:
                break

            chunk_identifier = identifier_bytes.decode(ENCODING)

            # if chunk_identifier == "afsp":
            # self._skip_afsp()
            # continue

            match chunk_identifier:
                # For cases other than default, the true sizes
                # of the chunks are stored in the 'ds64' chunk
                case "data":
                    self.stream.read(4)
                    chunk_size = data_low_size + (data_high_size << 32)
                case "fact":
                    self.stream.read(4)
                    chunk_size = sample_low_count + (sample_high_count << 32)
                case _:
                    size_bytes = self.stream.read(4)
                    if len(size_bytes) < 4:
                        break

                    chunk_size = int.from_bytes(size_bytes, byteorder=self.byteorder)

            if chunk_size % 2 != 0 and chunk_identifier != "bext":
                chunk_size += 1

            # Solves the performance issue (if the user opts in).
            # The stream.read() call on an RF64 file is obscene.
            # The chunk_data is never used after being returned, anyways.
            if self.ignore_chunks and chunk_identifier in self.ignore_chunks:
                chunk_data = b""
            else:
                chunk_data = self.stream.read(chunk_size)

            if chunk_identifier != NULL_IDENTIFIER:
                self.chunk_identifiers.append(chunk_identifier)
                yield (chunk_identifier, chunk_size, chunk_data)

            self.stream.seek(chunk_size - len(chunk_data), 1)
