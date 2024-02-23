ARG PYTHON_IMAGE=python:3.11.7-slim-bookworm


FROM $PYTHON_IMAGE as build

RUN pip install pdm
COPY ./pyproject.toml ./pdm.lock ./
RUN pdm export --prod -f requirements -o requirements.txt


FROM $PYTHON_IMAGE
ENV PYTHONPATH=$PYTHONPATH:/app/src \
    PATH=$PATH:/home/app/.local/bin \
    PYTHONUNBUFFERED=1

RUN addgroup --gid 2000 app && adduser --gid 2000 --uid 1000 app
USER app

WORKDIR /app

COPY --from=build ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --user --no-dependencies

COPY ./src ./src
COPY alembic.ini ./
ENTRYPOINT ["uvicorn", "app.adapters.api.app:create_app", "--factory", "--loop", "uvloop", "--host", "0.0.0.0"]
