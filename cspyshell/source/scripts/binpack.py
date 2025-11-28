import sys
import zlib
from collections.abc import Buffer
from typing import NoReturn, cast

Vector = tuple[
    int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int
]


class Binpack:
    _vector: Vector

    def __init__(self, iv: Vector) -> None:
        self._vector = iv

    def _next(self) -> Vector:
        values = list(
            (((value + (i * 7)) >> 5) | (((value + (i * 5)) & 31) << 3))
            for i, value in enumerate(self._vector)
        )

        for i, value in enumerate(self._vector):
            source, target = i, value & 0xF
            values[source], values[target] = values[target], values[source]

        self._vector = cast(Vector, tuple(values))
        return self._vector

    def crypt(self, buf: Buffer) -> bytes:
        buf = memoryview(buf)
        result = bytearray()

        while buf:
            block, buf = buf[:16], buf[16:]

            block = (ch ^ k for ch, k in zip(block, self._vector))
            result.extend(block)

            self._next()

        return memoryview(result)

    def pack(self, buf: Buffer) -> bytes:
        result = self.crypt(buf)
        compressed = zlib.compress(result)
        return compressed

    def unpack(self, buf: Buffer) -> bytes:
        uncompressed = zlib.decompress(buf)
        result = self.crypt(uncompressed)
        return result


def pack(buf: Buffer, iv: Vector) -> bytes:
    packer = Binpack(iv)
    return packer.pack(buf)


def unpack(buf: Buffer, iv: Vector) -> bytes:
    packer = Binpack(iv)
    return packer.unpack(buf)


def report(msg: str) -> NoReturn:
    print(msg, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 5:
        report(f"usage: {sys.argv[0]} pack/unpack [iv] [input] [output]")

    cmd, iv, inp, out = sys.argv[1:]

    iv = tuple(map(int, iv.split(",")))
    if len(iv) != 16 or not all(0 <= val <= 255 for val in iv):
        report("invalid iv.")

    with open(inp, "rb") as fp:
        data = fp.read()

    match cmd:
        case "pack":
            data = pack(data, iv)
        case "unpack":
            data = unpack(data, iv)

    with open(out, "wb") as fp:
        fp.write(data)


if __name__ == "__main__":
    main()
