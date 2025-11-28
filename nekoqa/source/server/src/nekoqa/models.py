import re
from typing import Self
from uuid import UUID

from pydantic import BaseModel, TypeAdapter, model_validator


class Problem(BaseModel):
    id: UUID
    question: str
    validation: str
    answers: list[str]

    @model_validator(mode="after")
    def validate_answers(self) -> Self:
        if not all(re.fullmatch(self.validation, answer) for answer in self.answers):
            raise ValueError(
                f"not all value match the validation '{self.validation}' in problem '{self.id}'"
            )
        return self


class Config(BaseModel):
    title: str
    problems: list[Problem]
    result: str
    show_failed: bool = True
    report: str | None = None

    @model_validator(mode="after")
    def validate_unique_id(self) -> Self:
        problems = list(problem for problem in self.problems)
        ids = set(problem.id for problem in problems)

        if len(ids) < len(problems):
            raise ValueError("duplicate problem id found.")

        return self


class AnswerSubmission(BaseModel):
    problem: UUID
    answer: str


SubmissionForm = TypeAdapter(list[AnswerSubmission])


class SubmissionResponse(BaseModel):
    success: bool
    message: str = ""
    failed: list[UUID] | None = None
