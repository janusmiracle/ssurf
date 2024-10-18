from io import BytesIO, BufferedReader

from ._errors import UnknownFormatError
from ._types import Stream
from .signatures import Identity, SIGNATURES
from .stream import ByteSource, BinarySource, FileSource


class Detect:

    def __init__(self, stream: Stream):
        self._stream = stream

    @property
    def stream(self):
        return self._stream

    def detect(self) -> Identity:
        """Detects the format of the given stream."""
        if not isinstance(
            self.stream, (BytesIO, BufferedReader, ByteSource, BinarySource, FileSource)
        ):
            raise TypeError("Invalid stream-type: {type(stream)}")

        try:
            return self.surface_detection()
        except UnknownFormatError:

            raise UnknownFormatError(
                "The provided stream is either corrupted, non-standard, or not WAVE."
            )

    def surface_detection(self) -> Identity:
        """Perform surface-level file format detection."""
        for signature in SIGNATURES:
            self.stream.seek(signature.offset)
            identifier = self.stream.read(signature.size)

            if identifier == signature.identifier[: signature.size]:
                # Determine if there's a sub-signature/form-type
                if len(signature.identifier) > signature.size:
                    remaining_bytes = signature.identifier[signature.size :]
                    self.stream.seek(signature.soffset)
                    sub_signature = self.stream.read(len(remaining_bytes))

                    if remaining_bytes == sub_signature:
                        return signature.identity
                else:
                    return signature.identity  # No sub-signature

        raise UnknownFormatError
