FROM node:20.2.0-alpine3.18 as frontend
ARG TARGETARCH

WORKDIR /repo

COPY . .

RUN npm ci && npm run build

FROM python:3.11.3-alpine3.18 as backend
ARG TARGETARCH

RUN apk add --no-cache gcc musl-dev postgresql-dev python3-dev

RUN adduser --disabled-password --uid 1000 acronyms \
    && mkdir /app \
    && chown acronyms:acronyms /app

USER acronyms
WORKDIR /app
ENV \
    HOME=/home/acronyms \
    PATH="/home/acronyms/.local/bin:${PATH}"

COPY --chown=acronyms . "${HOME}/repo"
COPY --chown=acronyms --from=frontend \
    /repo/backend/acronyms/web "${HOME}/repo/backend/acronyms/web"

# hadolint ignore=DL3013
RUN pip install --no-cache-dir --user "${HOME}/repo" \
    && rm -fr "${HOME}/repo"

USER root
RUN apk del gcc musl-dev postgresql-dev python3-dev

USER acronyms
EXPOSE 8000
ENTRYPOINT ["acronyms", "--host", "0.0.0.0"]
