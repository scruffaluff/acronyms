FROM python:3.11.4-alpine3.18
ARG TARGETARCH

RUN apk add --no-cache bash curl gcc musl-dev nodejs npm poetry postgresql-dev \
    python3-dev

RUN adduser --disabled-password --uid 10000 acronyms \
    && mkdir /app \
    && chown acronyms:acronyms /app

USER acronyms
ENV \
    HOME='/home/acronyms' \
    PATH="/home/acronyms/.local/bin:${PATH}" \
    POETRY_VIRTUALENVS_IN_PROJECT='true' \
    SHELL='/bin/sh'
WORKDIR /app
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN curl --fail --location --show-error --silent \
    https://get.pnpm.io/install.sh | ENV="${HOME}/.bashrc" bash

COPY --chown=acronyms . /app

# hadolint ignore=SC1091
RUN source "${HOME}/.bashrc" && pnpm install --frozen-lockfile \
    && poetry install --only main

EXPOSE 8000
ENTRYPOINT ["npm", "run", "dev"]
