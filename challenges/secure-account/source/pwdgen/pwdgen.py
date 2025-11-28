#!/usr/bin/env python3

import socket
import struct
from argparse import ArgumentParser
from enum import IntEnum

DEFAULT_SERVER_ADDR = "/run/pwdgen.sock"

DEFAULT_PASSWORD_LENGTH = 32


class StatusCode(IntEnum):
    OK = 0x00
    ERR = 0x01
    INV = 0x02
    UNDEF = 0x03


class PwdgenError(Exception):
    code: StatusCode
    message: bytes

    def __init__(self, code: StatusCode, message: bytes) -> None:
        self.code = code
        self.message = message

        super().__init__(message)


class PwdgenClient:
    _sock: socket.socket

    def __init__(self) -> None:
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def connect(self, addr: str = DEFAULT_SERVER_ADDR) -> None:
        self._sock.connect(addr)

    def _send(self, cmdline: bytes) -> None:
        if b"\n" in cmdline:
            raise ValueError

        self._sock.sendall(cmdline + b"\n")

    def _recv(self) -> bytes:
        header = self._sock.recv(3)
        code, length = struct.unpack(">BH", header)

        code = StatusCode(code)
        message = self._sock.recv(length)

        if code != StatusCode.OK:
            raise PwdgenError(code, message)

        return message

    def gen(self, length: int | None = None) -> bytes:
        if length == 0 or (length and length > 0xFFFF):
            raise ValueError

        args = [b"gen"]
        if length:
            args.append(str(length).encode())

        cmdline = b" ".join(args)
        self._send(cmdline)

        password = self._recv()
        return password

    def close(self) -> None:
        self._sock.close()

    def __enter__(self) -> "PwdgenClient":
        return self

    def __exit__(self, *_) -> None:
        self._sock.close()


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--addr", "-s", default=DEFAULT_SERVER_ADDR, help="server address to connect"
    )
    parser.add_argument(
        "--length",
        "-l",
        default=DEFAULT_PASSWORD_LENGTH,
        help="length of password to generate",
        type=int,
    )
    args = parser.parse_args()

    with PwdgenClient() as client:
        client.connect(args.addr)

        password = client.gen(args.length).decode("ascii")
        print(password)


if __name__ == "__main__":
    main()
