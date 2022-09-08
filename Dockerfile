FROM node:18.1.0 as frontend

WORKDIR /repo

COPY frontend/package*.json ./

RUN npm install

COPY frontend .

RUN npm run build

FROM python:3.9.12

ARG TARGETARCH

RUN adduser --uid 1000 acronyms

COPY backend /repo

# hadolint ignore=DL3013
RUN pip install --no-cache-dir /repo \
    && rm -fr /repo

USER acronyms
WORKDIR /app

COPY --chown=acronyms --from=frontend /repo/dist /app

EXPOSE 8000
ENTRYPOINT ["acronyms", "--host", "0.0.0.0", "--port", "8000"]
