FROM node:20.2.0-alpine3.17 as frontend
ARG TARGETARCH

WORKDIR /repo

COPY . .

RUN npm ci && npm run build

FROM python:3.11.3-alpine3.17 as backend
ARG TARGETARCH

RUN apk add --no-cache gcc libffi-dev musl-dev postgresql-dev python3-dev

RUN adduser --disabled-password --uid 10000 acronyms \
    && mkdir /app \
    && chown acronyms:acronyms /app

USER acronyms
WORKDIR /app
ENV \
    HOME=/home/acronyms \
    PATH="/home/acronyms/.local/bin:${PATH}"

COPY --chown=acronyms . "${HOME}/repo"
COPY --chown=acronyms --from=frontend \
    /repo/src/acronyms/web "${HOME}/repo/src/acronyms/web"

# hadolint ignore=DL3013
RUN pip install --no-cache-dir --user "${HOME}/repo" \
    && rm -fr "${HOME}/repo"

USER root
RUN apk del gcc musl-dev postgresql-dev python3-dev

USER acronyms
EXPOSE 8000
ENTRYPOINT ["acronyms", "--host", "0.0.0.0"]
