FROM node:18.10.0 as frontend

WORKDIR /repo

COPY . .

RUN npm ci && npm run build

FROM python:3.10.8

ARG TARGETARCH

RUN adduser --uid 1000 acronyms

USER acronyms
WORKDIR /app
ENV PATH="/home/acronyms/.local/bin:${PATH}"

COPY --chown=acronyms --from=frontend /repo/dist /app/dist
COPY --chown=acronyms . /repo

# Temporarily commented out for testing.
# # hadolint ignore=DL3013
# RUN pip install --no-cache-dir --user /repo

# USER root
# RUN rm -fr /repo

# USER acronyms

USER root
RUN pip install --no-cache-dir /repo && rm -fr /repo

EXPOSE 8000
ENTRYPOINT ["acronyms", "--host", "0.0.0.0", "--port", "8000"]
