import os
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pacman import BaseSettings, Context, Direction, Game, Settings, Size2D


app = FastAPI(openapi_url=None)
app.state.pacman = None

settings = Settings(
    canvas_size=Size2D(x=32, y=32), ghost_move_away_threshold=0.8, new_dot_threshold=0.75
)
gift_score = 300
gift = os.environ.get("A1CTF_FLAG", "flag{your-secret-key-here}")


def pacman_dep() -> Game:
    pacman = app.state.pacman
    if pacman is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    return pacman


PacmanDep = Annotated[Game, Depends(pacman_dep)]


class NextBody(BaseModel):
    direction: Direction | None = None


@app.post("/start")
def start_route() -> BaseSettings:
    app.state.pacman = Game(settings)
    return settings


@app.post("/next")
def next_route(pacman: PacmanDep, body: NextBody) -> Context:
    if body.direction is not None:
        pacman.context.direction = body.direction
    return next(pacman, pacman.context)


@app.get("/gift")
def gift_route(pacman: PacmanDep) -> PlainTextResponse:
    if pacman.context.score >= gift_score:
        return PlainTextResponse(gift)
    return PlainTextResponse("No gift for you.")


app.mount("/", StaticFiles(directory="static", html=True))
