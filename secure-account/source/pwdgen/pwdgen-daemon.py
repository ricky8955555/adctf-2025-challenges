#!/usr/bin/env python3

import base64
import contextlib
import os
import random
import struct
from argparse import ArgumentParser
from enum import IntEnum
from socketserver import StreamRequestHandler, ThreadingMixIn, UnixStreamServer
from typing import Any, Callable

DEFAULT_SERVER_ADDR = "/run/pwdgen.sock"

DEFAULT_PASSWORD_LENGTH = 32


class InvalidRequest(Exception):
    message: bytes

    def __init__(self, message: bytes) -> None:
        self.message = message

        super().__init__(message)


class StatusCode(IntEnum):
    OK = 0x00
    ERR = 0x01
    INV = 0x02
    UNDEF = 0x03


class Handler(StreamRequestHandler):
    handlers: dict[bytes, Callable[[bytes], bytes]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.handlers = {
            b"gen": self._gen,
        }

        super().__init__(*args, **kwargs)

    def _gen(self, args: bytes) -> bytes:
        length = int(args) if args else DEFAULT_PASSWORD_LENGTH

        if length > 0xFFFF:
            raise InvalidRequest(b"length too big.")

        rawlen = int(length / 5 * 4)
        raw = random.randbytes(rawlen)
        password = base64.b85encode(raw)[:length]  # make it ascii printable
        return password

    def _send(self, code: StatusCode, message: bytes) -> None:
        length = len(message)

        if length > 0xFFFF:
            raise ValueError

        header = struct.pack(">BH", code.value, length)
        message = header + message
        self.wfile.write(message)

    def handle(self) -> None:
        while True:
            message = self.rfile.readline().strip()
            if not message:
                return

            cmd, args, *_ = message.split(b" ", 1) + [b""]
            handler = self.handlers.get(cmd)

            if not handler:
                self._send(StatusCode.UNDEF, b"undefined command.")
                continue

            try:
                message = handler(args)
            except InvalidRequest as ex:
                self._send(StatusCode.INV, ex.message)
                continue
            except Exception as ex:
                self._send(StatusCode.ERR, str(ex).encode())
                continue

            self._send(StatusCode.OK, message)


class ThreadedUnixStreamServer(ThreadingMixIn, UnixStreamServer):
    pass


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--bind", "-b", default=DEFAULT_SERVER_ADDR, help="server address to bind")
    args = parser.parse_args()

    with contextlib.suppress(OSError):
        os.unlink(args.bind)

    with ThreadedUnixStreamServer(args.bind, Handler) as server:
        os.chmod(args.bind, 0o666)
        server.serve_forever()


if __name__ == "__main__":
    main()
