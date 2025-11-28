def crypt(content: bytes, key: int) -> bytes:
    assert key.bit_length() <= 32

    result = bytearray()
    shift = 0

    for i in range(0, len(content), 4):
        key_arr = key.to_bytes(4, byteorder="little")
        result.extend(c ^ k for c, k in zip(content[i:], key_arr))
        shift = (shift + 5) % 32
        key ^= (((key << shift) & 0xffffffff) | (key >> (32 - shift))) | (1 << shift)

    return bytes(result)


def djb2_hash(content: bytes) -> int:
    result = 5381

    for b in content:
        result = (((result << 5) + result) + b) & 0xffffffff

    return result


FLAG = b"flag{@_v3rY_s1Mp13_eNcR7pT_t7aT_y0U_c@n_kN0w7_p1@iNt3x7_aT7Ack!}"

print(", ".join(map(hex, crypt(FLAG, djb2_hash(FLAG)))))
