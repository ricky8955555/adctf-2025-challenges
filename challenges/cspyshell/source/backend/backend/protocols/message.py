from collections.abc import Buffer
from itertools import count

from .typing import UnsizedProtocolLayer


class MessageLayer:
    _underlying: UnsizedProtocolLayer

    def __init__(self, underlying: UnsizedProtocolLayer) -> None:
        self._underlying = underlying

    @property
    def underlying(self) -> UnsizedProtocolLayer:
        return self._underlying

    def _recv_varint(self) -> int:
        num = 0

        for i in count():
            byte, *_ = self._underlying.recv(1)

            num |= (byte & 127) << (i * 7)
            if byte < 128:
                break

        return num

    def _write_varint(self, num: int) -> None:
        buf = bytearray()

        while num:
            byte = num & 127

            if num >= 128:
                byte |= 128

            buf.append(byte)

            num >>= 7

        self._underlying.sendall(buf)

    def recv(self) -> bytes:
        size = self._recv_varint()
        return self._underlying.recv(size)

    def send(self, data: Buffer) -> None:
        data = memoryview(data)
        size = len(data)

        self._write_varint(size)
        self._underlying.sendall(data)
