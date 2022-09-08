FROM node:18.8.0 as frontend

WORKDIR /repo

COPY . .

RUN npm install && npm run build

FROM python:3.10.7

ARG TARGETARCH

RUN adduser --uid 1000 acronyms

COPY . /repo

# hadolint ignore=DL3013
RUN pip install --no-cache-dir /repo \
    && rm -fr /repo

USER acronyms
WORKDIR /app

COPY --chown=acronyms --from=frontend /repo/dist /app/dist

EXPOSE 8000
ENTRYPOINT ["acronyms", "--host", "0.0.0.0", "--port", "8000"]
