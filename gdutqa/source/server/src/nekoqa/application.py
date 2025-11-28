import pydantic_yaml
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from .models import Config, SubmissionForm, SubmissionResponse


def _load_config(path: str) -> Config:
    with open(path, "r", encoding="utf-8") as fp:
        return pydantic_yaml.parse_yaml_file_as(Config, fp)


templates = Jinja2Templates(directory="templates")

config = _load_config("config.yml")


async def homepage(request: Request) -> Response:
    return templates.TemplateResponse(
        request,
        "index.html",
        context={
            "title": config.title,
            "problems": config.problems,
        },
    )


async def submit(request: Request) -> Response:
    form_bytes = await request.body()

    try:
        form = SubmissionForm.validate_json(form_bytes)
    except ValidationError:
        return PlainTextResponse(
            SubmissionResponse(success=False, message="invalid form.").model_dump_json(),
            status_code=400,
        )

    submitted = set(submission.problem for submission in form)

    if len(submitted) < len(form):
        return PlainTextResponse(
            SubmissionResponse(
                success=False, message="duplicated question found."
            ).model_dump_json(),
            status_code=400,
        )

    problems = {problem.id: problem for problem in config.problems}
    if len(submitted) < len(problems) or submitted != set(problems.keys()):
        return PlainTextResponse(
            SubmissionResponse(success=False, message="invalid problem found.").model_dump_json(),
            status_code=400,
        )

    async def report() -> None:
        if config.report is not None:
            import httpx

            async with httpx.AsyncClient() as client:
                await client.post(config.report, content=form_bytes)

    report_task = BackgroundTask(report)

    failed = [
        submission.problem
        for submission in form
        if submission.answer not in problems[submission.problem].answers
    ]

    if failed:
        message = "some answers incorrect."
    else:
        message = config.result

    return PlainTextResponse(
        SubmissionResponse(
            success=not failed, message=message, failed=failed if config.show_failed else None
        ).model_dump_json(),
        background=report_task,
    )


routes = [Route("/", homepage), Route("/submit", submit, methods=["POST"])]

app = Starlette(routes=routes)
