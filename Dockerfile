FROM node:20.4.0-alpine3.18 as frontend
ARG TARGETARCH

WORKDIR /repo

COPY . .

RUN corepack enable pnpm && pnpm install --frozen-lockfile && pnpm build

FROM python:3.11.4-alpine3.18 as backend
ARG TARGETARCH

RUN apk add --no-cache gcc libffi-dev musl-dev postgresql-dev python3-dev

RUN adduser --disabled-password --uid 10000 acronyms \
    && mkdir /app \
    && chown acronyms:acronyms /app

USER acronyms
ENV \
    HOME='/home/acronyms' \
    PATH="/home/acronyms/.local/bin:${PATH}"
WORKDIR /app

COPY --chown=acronyms . "${HOME}/repo"
COPY --chown=acronyms --from=frontend \
    /repo/src/acronyms/web "${HOME}/repo/src/acronyms/web"

# hadolint ignore=DL3013
RUN pip install --no-cache-dir --user "${HOME}/repo" \
    && rm -fr "${HOME}/repo"

USER acronyms
EXPOSE 8000
ENTRYPOINT ["acronyms", "--host", "0.0.0.0"]
