import secrets
import struct
from collections.abc import Buffer
from typing import Self

from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA512
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .typing import UnsizedProtocolLayer


class SecureLayer:
    _underlying: UnsizedProtocolLayer
    _cipher: AESGCM
    _buffer: bytearray

    def __init__(self, underlying: UnsizedProtocolLayer, cipher: AESGCM) -> None:
        self._underlying = underlying
        self._cipher = cipher
        self._buffer = bytearray()

    @property
    def underlying(self) -> UnsizedProtocolLayer:
        return self._underlying

    @classmethod
    def initiate_connection(
        cls, underlying: UnsizedProtocolLayer, key: X25519PrivateKey
    ) -> Self:
        my_public_key = key.public_key()
        my_public_key_bytes = my_public_key.public_bytes_raw()
        underlying.sendall(my_public_key_bytes)

        other_public_key_bytes = underlying.recv(32)
        other_public_key = X25519PublicKey.from_public_bytes(other_public_key_bytes)

        shared_secret = key.exchange(other_public_key)

        hasher = SHA512()
        kdf = HKDF(hasher, 32, None, None)

        symmetric_key = kdf.derive(shared_secret)
        cipher = AESGCM(symmetric_key)

        return cls(underlying, cipher)

    @staticmethod
    def _encrypt_nonce(nonce: Buffer) -> bytes:
        nonce = memoryview(nonce)

        if not nonce:
            return b""

        result = bytearray()

        result.append(nonce[0])
        for ch in nonce[1:]:
            result.append(ch ^ result[-1])

        return bytes(result)

    @staticmethod
    def _decrypt_nonce(nonce: Buffer) -> bytes:
        nonce = memoryview(nonce)

        if not nonce:
            return b""

        result = bytes((nonce[0], *(a ^ b for a, b in zip(nonce, nonce[1:]))))
        return bytes(result)

    def _recv_block(self) -> None:
        header = self._underlying.recv(13)
        nonce, size = struct.unpack(">12sB", header)

        nonce = self._decrypt_nonce(nonce)
        ciphertext = self._underlying.recv(size + 16)

        plaintext = self._cipher.decrypt(nonce, ciphertext, None)

        self._buffer.extend(plaintext)

    def recv(self, bufsize: int) -> bytes:
        while len(self._buffer) < bufsize:
            self._recv_block()

        buffer = memoryview(self._buffer[:bufsize])
        self._buffer = self._buffer[bufsize:]

        return buffer

    def sendall(self, data: Buffer) -> None:
        data = memoryview(data)

        while data:
            plaintext, data = data[:255], data[255:]

            size = len(plaintext)

            nonce = secrets.token_bytes(12)
            ciphertext = self._cipher.encrypt(nonce, plaintext, None)

            nonce = self._encrypt_nonce(nonce)

            packed = struct.pack(">12sB", nonce, size)
            packed += ciphertext

            self._underlying.sendall(packed)
