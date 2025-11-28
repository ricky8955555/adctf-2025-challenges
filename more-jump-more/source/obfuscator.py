import random
import re
import sys
from dataclasses import dataclass, field
from random import Random
from typing import IO

GLOBAL_LABEL_PATTERN = re.compile(r"^(?P<name>[^\.\s]\S*):$")
LOCAL_LABEL_PATTERN = re.compile(r"^\.(?P<name>\S+):$")
CODE_PATTERN = re.compile(r"^[ \t]+(?P<code>.+)(?:\s*;.*)$")
COMMENT_PATTERN = re.compile(r"^;")


@dataclass(kw_only=True)
class ObfuscateContext:
    global_name: str
    completed: bool = False
    redirected_labels: dict[str, int] = field(default_factory=dict[str, int])
    pending_labels: list[str] = field(default_factory=list[str])
    snippets: list[str] = field(default_factory=list[str])

    def feed_label(self, label: str) -> None:
        label = label.strip().removeprefix(".")
        self.pending_labels.append(label)

    def feed_snippet(self, code: str) -> None:
        code = code.strip()

        if self.pending_labels:
            idx = len(self.snippets)
            self.redirected_labels.update({label: idx for label in self.pending_labels})
            self.pending_labels.clear()

        if self.snippets and code.startswith("j"):  # treat all j-prefix code as jump
            self.snippets[-1] += f"\n{code}"  # combine to last line
        else:
            self.snippets.append(code)

    def complete(
        self,
        output: IO[str],
        *,
        indent: int = 4,
        rng: Random | None = None,
        label_prefix: str = "obfuscated_line_",
        register: str = "rax",
    ) -> None:
        self.completed = True

        if self.pending_labels:
            self.feed_snippet("")

        spaces = " " * indent

        snippets: list[str] = []

        for i, snippet in enumerate(self.snippets):
            code = ""

            for line in snippet.splitlines():
                operation = line.split(" ", 1)

                if len(operation) == 2:
                    inst, operand = operation

                    if ln := self.redirected_labels.get(operand.removeprefix(".")):
                        code += f"{spaces}{inst} .{label_prefix}{ln}\n"
                        continue

                code += f"{spaces}{line}\n"

            snippet = f"""
.{label_prefix}{i}:
{code}
{spaces}mov {register}, {i + 1}
{spaces}jmp .{label_prefix}dispatch
""".lstrip()

            snippets.append(snippet)

        output.write(f"{self.global_name}:\n")

        output.write(f"{spaces}xor {register}, {register}\n")  # clear register first.
        output.write(f"{spaces}jmp .{label_prefix}dispatch\n")  # jump to dispatch.

        if rng is None:
            random.shuffle(snippets)
        else:
            rng.shuffle(snippets)

        for snippet in snippets:
            output.write(snippet)

        output.write(f".{label_prefix}dispatch:\n")
        for i in range(len(snippets)):
            output.write(f"{spaces}cmp {register}, {i}\n{spaces}je .{label_prefix}{i}\n")


def obfuscate(
    code: IO[str],
    output: IO[str],
    *,
    indent: int = 4,
    rng: Random | None = None,
    label_prefix: str = "obfuscated_",
    register: str = "rax",
) -> None:
    context: ObfuscateContext | None = None

    while True:
        line = code.readline()
        if not line:
            break

        line = line.rstrip()

        if not line or COMMENT_PATTERN.match(line):
            continue

        if match := GLOBAL_LABEL_PATTERN.match(line):
            if context is not None:
                context.complete(
                    output, indent=indent, rng=rng, label_prefix=label_prefix, register=register
                )

            context = ObfuscateContext(global_name=match.group("name"))

        elif match := LOCAL_LABEL_PATTERN.match(line):
            if context is None:
                raise ValueError

            context.feed_label(match.group("name"))

        elif match := CODE_PATTERN.match(line):
            if context is None:
                raise ValueError

            context.feed_snippet(match.group("code").strip())

        else:
            output.write(line + "\n")

    if context is not None and not context.completed:
        context.complete(
            output, indent=indent, rng=rng, label_prefix=label_prefix, register=register
        )


def main() -> None:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} [infile] [outfile]", file=sys.stderr)
        sys.exit(1)

    infile, outfile = sys.argv[1:]

    with open(infile, "r") as infp, open(outfile, "w") as outfp:
        obfuscate(infp, outfp, register="r8")


if __name__ == "__main__":
    main()
