import traceback
from dataclasses import dataclass, field
from typing import Any, NoReturn

from .protocols.typing import SizedProtocolLayer


@dataclass
class Context:
    variables: dict[str, Any] = field(default_factory=dict[str, Any])


class Application:
    _sock: SizedProtocolLayer
    _context: Context

    def __init__(self, sock: SizedProtocolLayer) -> None:
        self._sock = sock
        self._context = Context()

    def handle(self, message: bytes) -> bytes:
        message = message.strip()

        if not message:
            return b""

        try:
            if b"\n" not in message:
                try:
                    val = eval(
                        message, self._context.variables, self._context.variables
                    )
                    return repr(val).encode("utf-8")
                except SyntaxError:
                    pass

            exec(message, self._context.variables, self._context.variables)
        except Exception:
            return traceback.format_exc().encode("utf-8")

        return b""

    def run(self) -> NoReturn:
        while True:
            message = self._sock.recv()
            response = self.handle(message)
            self._sock.send(response)
