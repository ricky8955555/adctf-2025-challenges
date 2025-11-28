from enum import IntEnum
from random import Random, SystemRandom
from typing import Generator, Self

from pydantic import BaseModel, ConfigDict, Field


class Direction(IntEnum):
    LEFT = 0b00
    RIGHT = 0b01
    UP = 0b10
    DOWN = 0b11


class Distance2D(BaseModel):
    x: int
    y: int

    def as_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)

    def __lt__(self, other: Distance2D) -> bool:
        return self.x < other.x and self.y < other.y

    def __le__(self, other: Distance2D) -> bool:
        return self.x <= other.x and self.y <= other.y

    def __gt__(self, other: Distance2D) -> bool:
        return self.x > other.x and self.y > other.y

    def __ge__(self, other: Distance2D) -> bool:
        return self.x >= other.x and self.y >= other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __sub__(self, other: Distance2D) -> Distance2D:
        return Distance2D(x=self.x - other.x, y=self.y - other.y)

    def __add__(self, other: Distance2D) -> Distance2D:
        return Distance2D(x=self.x + other.x, y=self.y + other.y)

    def __neg__(self) -> Distance2D:
        return Distance2D(x=-self.x, y=-self.y)

    def __pos__(self) -> Distance2D:
        return Distance2D(x=+self.x, y=+self.y)

    def __abs__(self) -> Distance2D:
        return Distance2D(x=abs(self.x), y=abs(self.y))

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    model_config = ConfigDict(frozen=True)


class Axis2D(Distance2D):
    x: int = Field(ge=0)
    y: int = Field(ge=0)

    def move(self, direction: Direction, *, step: int = 1, corner: Size2D | None = None) -> Axis2D:
        step *= ((direction & 0b1) << 1) - 1

        x, y = self.as_tuple()

        if direction & 0b10:
            y = max(y + step, 0)
        else:
            x = max(x + step, 0)

        if corner:
            x = min(x, corner.x - 1)
            y = min(y, corner.y - 1)

        return Axis2D(x=x, y=y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))


class Size2D(Axis2D):
    x: int = Field(gt=0)
    y: int = Field(gt=0)

    @property
    def axis_count(self) -> int:
        return self.x * self.y

    @property
    def end(self) -> Axis2D:
        return Axis2D.model_validate((self - Distance2D(x=1, y=1)).model_dump())

    def iter_axises(self) -> Generator[Axis2D, None, None]:
        return (Axis2D(x=x, y=y) for y in range(self.y) for x in range(self.x))

    def __contains__(self, axis: Axis2D) -> bool:
        return axis < self


class Context(BaseModel):
    pacman: Axis2D = Field(default_factory=lambda: Axis2D(x=0, y=0))
    direction: Direction = Direction.DOWN

    ghost: Axis2D

    dots: set[Axis2D] = Field(default_factory=set[Axis2D])

    score: int = 0
    alive: bool = True


class BaseSettings(BaseModel):
    canvas_size: Size2D = Field(default_factory=lambda: Size2D(x=32, y=32))
    ghost_move_away_threshold: float = Field(ge=0, le=1, default=0.9)
    new_dot_threshold: float = Field(ge=0, le=1, default=0.8)


class Settings(BaseSettings):
    random: Random = Field(default_factory=SystemRandom)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Game:
    _started: bool

    context: Context
    settings: Settings

    def __init__(self, settings: Settings | None = None) -> None:
        if settings is None:
            settings = Settings()

        self._started = False
        self.settings = settings
        self.context = Context(ghost=self.settings.canvas_size.end)

    def _random_position(self) -> Axis2D:
        x = self.settings.random.randrange(self.settings.canvas_size.x)
        y = self.settings.random.randrange(self.settings.canvas_size.y)
        return Axis2D(x=x, y=y)

    def _draw(self, threshold: float) -> bool:
        value = self.settings.random.random()
        return value > threshold

    def _move_ghost(self) -> None:
        diff = self.context.pacman - self.context.ghost

        move_away = self._draw(self.settings.ghost_move_away_threshold)
        if move_away:
            diff = -diff

        x_move = diff.x != 0
        y_move = diff.y != 0
        if x_move and y_move:
            x_move = self._draw(0.5)
            y_move = not x_move

        if diff.x and x_move:
            self.context.ghost = self.context.ghost.move(
                Direction.LEFT if diff.x < 0 else Direction.RIGHT,
                corner=self.settings.canvas_size,
            )
        if diff.y and y_move:
            self.context.ghost = self.context.ghost.move(
                Direction.UP if diff.y < 0 else Direction.DOWN,
                corner=self.settings.canvas_size,
            )

    def _new_dot(self) -> None:
        if not self._draw(self.settings.new_dot_threshold):
            return

        if len(self.context.dots) == self.settings.canvas_size.axis_count - 2:
            return

        all_axises = set(self.settings.canvas_size.iter_axises())

        available = all_axises.difference(self.context.dots)
        available = available.difference({self.context.ghost, self.context.pacman})

        index = self.settings.random.randint(1, len(available))
        axis_iter = iter(available)

        dot = None
        for _ in range(index):
            dot = next(axis_iter)
        assert dot is not None

        self.context.dots.add(dot)

    def _go_forward(self) -> None:
        self.context.pacman = self.context.pacman.move(
            self.context.direction, corner=self.settings.canvas_size
        )

    def _check_ghost_collision(self) -> bool:
        self.context.alive = self.context.pacman != self.context.ghost
        return not self.context.alive

    def _check_dot_collision(self) -> None:
        try:
            self.context.dots.remove(self.context.pacman)
        except KeyError:
            return

        self.context.score += 1

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Context:
        if not self._started:
            self._started = True
            return self.context

        if not self.context.alive:
            raise StopIteration

        self._go_forward()
        if self._check_ghost_collision():
            return self.context
        self._check_dot_collision()

        self._move_ghost()
        if self._check_ghost_collision():
            return self.context

        self._new_dot()

        return self.context
