import asyncio
import contextlib
import os
import posixpath
import subprocess
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import AsyncGenerator

from starlette.datastructures import Headers, MutableHeaders, QueryParams
from starlette.requests import Request
from starlette.responses import PlainTextResponse, StreamingResponse
from starlette.types import ASGIApp, Receive, Scope, Send


@dataclass(frozen=True, kw_only=True)
class _UGIResponseHeaders:
    status: int
    other: Headers


@dataclass(frozen=True, kw_only=True)
class _EnvsBuildResult:
    envs: dict[str, str]
    body_consumed: bool


class SlowUGI:
    directory: Path

    def __init__(self, directory: PathLike[str] | str) -> None:
        self.directory = Path(directory)

    @staticmethod
    def _safe_resolve_path(path: PathLike[str] | str) -> str:
        root_bound = posixpath.join("/", path)
        cleaned = posixpath.abspath(root_bound)
        resolved = posixpath.relpath(cleaned, "/")
        return resolved

    def _get_path(self, scope: Scope) -> Path:
        root_path = scope.get("root_path", "")
        path = posixpath.relpath(scope["path"], root_path)

        resolved_path = self._safe_resolve_path(path)
        return self.directory.joinpath(resolved_path)

    @staticmethod
    async def _build_envs(request: Request) -> _EnvsBuildResult:
        def to_env_name(name: str, *, prefix: str | None = None) -> str:
            if prefix:
                name = f"{prefix}_{name}"

            return name.replace("-", "_").upper()

        # common envs
        envs = {
            "METHOD": request.method,
            "URL_PATH": request.url.path,
        }

        # queries
        envs.update(
            {
                to_env_name(key, prefix="query"): str(value)
                for key, value in request.query_params.items()
            }
        )

        headers = request.headers.mutablecopy()

        cookie = headers.get("Cookie", "")
        for item in cookie.split(";"):
            item = item.strip()

            name, _, value = item.partition("=")
            name = to_env_name(name, prefix="cookie")

            envs[name] = value

        with contextlib.suppress(KeyError):
            del headers["Cookie"]

        # headers
        envs.update({to_env_name(key): value for key, value in request.headers.items()})

        consumed = False

        if headers.get("Content-Type") == "application/x-www-form-urlencoded":
            body = await request.body()
            params = QueryParams(body)
            envs.update(
                {
                    to_env_name(key, prefix="body"): str(value)
                    for key, value in params.items()
                }
            )

            consumed = True

        return _EnvsBuildResult(envs=envs, body_consumed=consumed)

    async def _forward_to_ugi(self, path: Path, request: Request) -> ASGIApp:
        envs = os.environ.copy()

        built_envs = await self._build_envs(request)
        envs.update(built_envs.envs)

        process = subprocess.Popen(
            path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=False,
            env=envs,
        )

        async def read_headers() -> _UGIResponseHeaders:
            assert process.stdout is not None, "stdout should not be None."

            headers = MutableHeaders()

            while True:
                line = await asyncio.to_thread(process.stdout.readline)
                line = line.decode("utf-8").rstrip()

                if not line:
                    break

                name, _, value = line.partition(":")
                value = value.lstrip()

                headers[name] = value

            status = int(headers.get("Status", "200"))

            with contextlib.suppress(KeyError):
                del headers["Status"]

            return _UGIResponseHeaders(status=status, other=headers)

        async def feed() -> None:
            assert process.stdin is not None, "stdin should not be None."

            async for data in request.stream():
                await asyncio.to_thread(process.stdin.write, data)

            process.stdin.close()

        async def stream() -> AsyncGenerator[bytes, None]:
            assert process.stdout is not None, "stdout should not be None."

            while True:
                buffer = await asyncio.to_thread(process.stdout.read, 1024)

                if not buffer:
                    break

                yield buffer

        if not built_envs.body_consumed:
            await feed()

        headers = await read_headers()
        return StreamingResponse(stream(), headers.status, headers.other)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        assert scope["type"] == "http"

        path = self._get_path(scope)

        if path.exists():
            if path.is_dir():
                response = PlainTextResponse("Forbidden", 403)
            else:
                request = Request(scope, receive, send)
                response = await self._forward_to_ugi(path, request)
        else:
            response = PlainTextResponse("Not Found", 404)

        await response(scope, receive, send)
