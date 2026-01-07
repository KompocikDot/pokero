FROM python:3.13

EXPOSE 8000

ENV PATH="/backend/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Copying uv for ease of development.
COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

WORKDIR /backend

# Base directory where this dockerfile is called is project root.
COPY ./uv.lock .
COPY ./pyproject.toml .
COPY ./app/ ./app

RUN uv sync

WORKDIR /backend/app

RUN python manage.py tailwind install && \
	python manage.py tailwind build && \
	python manage.py collectstatic

RUN useradd -m -u 1000 appuser

USER appuser

CMD ["gunicorn", "--log-level", "debug", "-b", "0.0.0.0:8000", "app.wsgi:application"]
