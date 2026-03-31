FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md /app/

RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -e .[train]

COPY rocketclaw /app/rocketclaw

RUN useradd -ms /bin/bash rocket
USER rocket

ENV ROCKETCLAW_HOME=/home/rocket/.rocketclaw

ENTRYPOINT ["rocketclaw"]
