import ctypes
import struct
import sys


def next_block(block: list[int], key: bytes) -> None:
    target = 0

    for k in key:
        for source in range(256):
            target = (target + k) & 0xFF

            block[source], block[target] = block[target], block[source]


def init_block() -> list[int]:
    return list(range(256))


def tea_encrypt(v: tuple[int, int], k: tuple[int, int, int, int]) -> tuple[int, int]:
    v0 = ctypes.c_uint32(v[0])
    v1 = ctypes.c_uint32(v[1])
    sum = ctypes.c_uint32(0)

    for _ in range(32):
        sum.value += 0x9E3779B9
        v0.value += ((v1.value << 4) + k[0]) ^ (v1.value + sum.value) ^ ((v1.value >> 5) + k[1])
        v1.value += ((v0.value << 4) + k[2]) ^ (v0.value + sum.value) ^ ((v0.value >> 5) + k[3])

    return (v0.value, v1.value)


def encrypt(plaintext: bytes, key: bytes) -> bytes:
    if len(plaintext) % 8 != 0:
        raise ValueError

    raw_block = init_block()
    block: list[int] = []

    ciphertext = bytearray()

    for i in range(0, len(plaintext), 8):
        block = block[16:]
        if not block:
            next_block(raw_block, key)
            block = raw_block

        v = struct.unpack("<II", plaintext[i : i + 8])
        k = struct.unpack("<IIII", bytes(block[:16]))

        result = tea_encrypt(v, k)
        ciphertext.extend(b for num in result for b in num.to_bytes(4, "little"))

    return ciphertext


def format_bytes(b: bytes) -> str:
    return ", ".join(f"0x{byte:02x}" for byte in b)


def main() -> None:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} [plaintext] [key]", file=sys.stderr)
        return

    plaintext, key = (val.encode("utf-8") for val in sys.argv[1:])

    length = len(plaintext)
    plaintext = plaintext.ljust(length + ((8 - (length % 8)) % 8), b"\0")

    ciphertext = encrypt(plaintext, key + b"\0")
    print("key:", format_bytes(key))
    print("ciphertext:", format_bytes(ciphertext))


if __name__ == "__main__":
    main()
