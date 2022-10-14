FROM node:18.10.0 as frontend

WORKDIR /repo

COPY . .

RUN npm ci && npm run build

FROM python:3.10.8

ARG TARGETARCH

RUN adduser --disabled-password --uid 1000 acronyms \
    && mkdir /app \
    && chown acronyms:acronyms /app

USER acronyms
WORKDIR /app
ENV \
    HOME=/home/acronyms \
    PATH="/home/acronyms/.local/bin:${PATH}"

COPY --chown=acronyms --from=frontend /repo/dist /app/dist
COPY --chown=acronyms . "${HOME}/repo"

# hadolint ignore=DL3013
RUN pip install --no-cache-dir --user "${HOME}/repo" \
    && rm -fr "${HOME}/repo"

EXPOSE 8000
ENTRYPOINT ["acronyms", "--host", "0.0.0.0", "--port", "8000"]
