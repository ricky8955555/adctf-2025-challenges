import re
import subprocess
import time
from random import SystemRandom
from typing import Sequence

SHELL_PATH = "dist/cspyshell"

WORD_PER_MINUTE = 70
WAIT_ERROR = 5


def strip_codes(codes: Sequence[str]) -> list[str]:
    return [
        "\n".join(filter(lambda line: line.strip(), code.splitlines()))
        for code in codes
    ]


CODES = strip_codes(
    [
        "import hashlib",
        """
def init_block(key: bytes) -> tuple[int, ...]:
    block = list(range(256))
    targets = hashlib.sha512(key).digest()
    new_targets = bytearray()

    for start in range(0, 256, 64):
        for i, byte in enumerate(targets):
            source, target = i + start, byte
            block[source], block[target] = block[target], block[source]

            new_targets.append(block[source] ^ byte)

        targets = bytes(new_targets)
        new_targets.clear()

    return block
        """,
        """
def encrypt(plaintext: bytes, block: tuple[int, ...]) -> bytes:
    result = bytearray()

    for i, ch in enumerate(plaintext):
        idx = i & 0xff
        byte = block[idx]

        ch ^= byte
        result.append(ch)

        block[idx], block[ch] = block[ch], block[idx]

    return bytes(result)
        """,
        """
with open("flag.txt", "rb") as fp:
    flag = fp.read().rstrip()
        """,
        "block = init_block(b'f0lloW p-mArU t7aNks m3ow.')",
        "ciphertext = encrypt(flag, block)",
        "ciphertext.hex()",
    ]
)


def main() -> None:
    random = SystemRandom()

    with subprocess.Popen(SHELL_PATH, stdin=subprocess.PIPE) as process:
        time.sleep(3)  # wait for start

        assert process.stdin is not None

        for code in CODES:
            print(code)

            process.stdin.write(code.encode("utf-8"))

            word_count = len(re.findall(r"[\w\d]+", code))
            wpm = WORD_PER_MINUTE + random.randint(-WAIT_ERROR, WAIT_ERROR)
            wait_for = (word_count / wpm) * 60

            print(f"{word_count=} {wpm=} {wait_for=:.2f}")

            time.sleep(wait_for)

            process.stdin.write(b"\n\n")
            process.stdin.flush()

        process.stdin.close()
        process.wait()


if __name__ == "__main__":
    main()
