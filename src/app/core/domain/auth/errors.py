import dataclasses

from jwt import PyJWTError


@dataclasses.dataclass
class TokenDecodeError:
    error: PyJWTError
