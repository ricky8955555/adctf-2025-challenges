import asyncio
import decimal
import operator
import os
from dataclasses import dataclass
from decimal import Decimal
from random import Random, SystemRandom
from typing import Callable, cast

# increase prec of decimal
decimal.getcontext().prec = 100


OperatorFunc = Callable[[Decimal, Decimal], Decimal]


@dataclass(frozen=True, kw_only=True)
class Operator:
    symbol: str
    func: OperatorFunc


@dataclass(frozen=True, kw_only=True)
class Expression:
    lhs: "Expression | Decimal"
    op: Operator
    rhs: "Expression | Decimal"

    def __str__(self) -> str:
        lhs = str(self.lhs)
        if isinstance(self.lhs, Expression):
            lhs = f"({lhs})"

        rhs = str(self.rhs)
        if isinstance(self.rhs, Expression):
            rhs = f"({rhs})"

        return f"{lhs} {self.op.symbol} {rhs}"

    def calculate(self) -> Decimal:
        lhs = self.lhs.calculate() if isinstance(self.lhs, Expression) else self.lhs
        rhs = self.rhs.calculate() if isinstance(self.rhs, Expression) else self.rhs
        return self.op.func(lhs, rhs)


def round_wrap(op: OperatorFunc, ndigits: int = 0) -> OperatorFunc:
    return lambda lhs, rhs: round(op(lhs, rhs), ndigits)


ROUND_NDIGITS = 10

OP_ADD = Operator(symbol="+", func=operator.add)
OP_SUB = Operator(symbol="-", func=operator.sub)
OP_MUL = Operator(symbol="*", func=round_wrap(operator.mul, ROUND_NDIGITS))
OP_DIV = Operator(symbol="/", func=round_wrap(operator.truediv, ROUND_NDIGITS))
OP_POW = Operator(symbol="^", func=round_wrap(operator.pow, ROUND_NDIGITS))


QuestionerFunc = Callable[[Random], Expression]


@dataclass(frozen=True, kw_only=True)
class Group:
    title: str
    count: int
    time_limit: float
    questioner: QuestionerFunc


def stage_easy(rng: Random) -> Expression:
    lhs, rhs = (Decimal(rng.randrange(1, 100)) for _ in range(2))
    op = rng.choice([OP_ADD, OP_SUB])
    return Expression(lhs=lhs, op=op, rhs=rhs)


def stage_normal(rng: Random) -> Expression:
    lhs, rhs = (Decimal(rng.randrange(1, 100)) for _ in range(2))
    op = rng.choice([OP_MUL, OP_DIV])
    return Expression(lhs=lhs, op=op, rhs=rhs)


def stage_hard(rng: Random) -> Expression:
    upper = 10000000
    deno = 1000

    expr = Decimal(rng.randrange(1, upper)) / deno

    for _ in range(5):
        rhs = Decimal(rng.randrange(1, upper)) / deno
        op = rng.choice([OP_ADD, OP_SUB, OP_MUL, OP_DIV])
        expr = Expression(lhs=expr, op=op, rhs=rhs)

    return cast(Expression, expr)


def stage_expert(rng: Random) -> Expression:
    lhs = Decimal(rng.randrange(5, 10))
    rhs = Decimal(rng.randrange(30, 50))
    first = Expression(lhs=lhs, op=OP_POW, rhs=rhs)

    lhs = Decimal(rng.randrange(5, 10))
    rhs = Decimal(rng.randrange(30, 50))
    second = Expression(lhs=lhs, op=OP_POW, rhs=rhs)

    expr = Expression(lhs=first, op=OP_DIV, rhs=second)
    return expr


def stage_master(rng: Random) -> Expression:
    first = stage_expert(rng)
    second = stage_expert(rng)
    expr = Expression(lhs=first, op=OP_ADD, rhs=second)

    rhs = stage_hard(rng)
    expr = Expression(lhs=expr, op=OP_ADD, rhs=rhs)

    return expr


GROUPS = [
    Group(
        title="一、100 以内整数加减运算题 (共 50 题) (请在 10s 内完成作答)",
        count=50,
        time_limit=10,
        questioner=stage_easy,
    ),
    Group(
        title="二、100 以内整数乘除运算题 (共 50 题) (请在 15s 内完成作答) (注: 每一步计算保留 10 位小数)",
        count=50,
        time_limit=15,
        questioner=stage_normal,
    ),
    Group(
        title="三、10000 以内有理数四则复合运算题 (共 100 题) (请在 30s 内完成作答) (注: 每一步计算保留 10 位小数)",
        count=100,
        time_limit=30,
        questioner=stage_hard,
    ),
    Group(
        title="四、整数幂运算题 (共 150 题) (请在 10s 内完成作答) (注: 每一步计算保留 10 位小数)",
        count=150,
        time_limit=10,
        questioner=stage_expert,
    ),
    Group(
        title="五、整数幂与四则复合运算题 (共 300 题) (请在 5s 内完成作答) (注: 每一步计算保留 10 位小数)",
        count=300,
        time_limit=5,
        questioner=stage_master,
    ),
]


FLAG = os.environ.get("A1CTF_FLAG", "flag{your-secret-key-here}")


async def main() -> None:
    rng = SystemRandom()

    for group in GROUPS:
        print(group.title)

        for idx in range(group.count):
            question = group.questioner(rng)
            expected_answer = str(question.calculate())

            print(f"{idx + 1}. {question} = ?")

            try:
                input_task = asyncio.to_thread(input)
                user_input = await asyncio.wait_for(input_task, group.time_limit)
            except TimeoutError:
                print("听不清楚，该罚！")
                return

            if user_input.strip() != expected_answer:
                print("答案错，该罚！")
                return

        print()

    print("你过关！")
    print(FLAG)


if __name__ == "__main__":
    asyncio.run(main())
