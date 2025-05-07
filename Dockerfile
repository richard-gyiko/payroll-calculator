FROM python:3.13-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

COPY pyproject.toml /code/pyproject.toml
COPY uv.lock /code/uv.lock

RUN uv sync --frozen

COPY . /code/

CMD ["uv", "run", "src/payroll_calculator/api.py"]
