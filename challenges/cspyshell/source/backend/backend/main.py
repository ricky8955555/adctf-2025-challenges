import socket
import sys
import zlib
from random import Random
from typing import Any

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from .application import Application
from .protocols.compression import CompressionLayer
from .protocols.message import MessageLayer
from .protocols.secure import SecureLayer


def generate_static_private_key(seed: Any) -> X25519PrivateKey:
    key_bytes = Random(seed).randbytes(32)
    key = X25519PrivateKey.from_private_bytes(key_bytes)
    return key


PRIVATE_KEY_SEED = bytes([
    0x0D, 0x00, 0x07, 0x21, 0x01, 0xBF, 0x52, 0x1D, 0x4B, 0x42, 0x11, 0x45, 0x14, 0x57, 0xA7, 0x00,
])
PRIVATE_KEY = generate_static_private_key(PRIVATE_KEY_SEED)


def main() -> None:
    address = sys.argv[1], int(sys.argv[2])
    tcp_layer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_layer.connect(address)

    secure_layer = SecureLayer.initiate_connection(tcp_layer, PRIVATE_KEY)
    message_layer = MessageLayer(secure_layer)
    compression_layer = CompressionLayer(message_layer, zlib)

    app = Application(compression_layer)
    app.run()
