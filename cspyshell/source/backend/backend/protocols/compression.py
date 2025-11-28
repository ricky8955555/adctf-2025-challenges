from collections.abc import Buffer
from typing import Protocol

from .typing import SizedProtocolLayer


class Compressor(Protocol):
    def compress(self, data: Buffer, /) -> bytes: ...
    def decompress(self, data: Buffer, /) -> bytes: ...


class CompressionLayer:
    _underlying: SizedProtocolLayer
    _compressor: Compressor

    def __init__(self, underlying: SizedProtocolLayer, compressor: Compressor) -> None:
        self._underlying = underlying
        self._compressor = compressor

    @property
    def underlying(self) -> SizedProtocolLayer:
        return self._underlying

    @property
    def compressor(self) -> Compressor:
        return self._compressor

    def recv(self) -> bytes:
        compressed = self._underlying.recv()
        data = self._compressor.decompress(compressed)
        return data

    def send(self, data: Buffer) -> None:
        compressed = self._compressor.compress(data)
        self._underlying.send(compressed)
