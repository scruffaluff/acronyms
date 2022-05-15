FROM python:3.9.12

ARG TARGETARCH

RUN adduser backend

COPY . /repo

# hadolint ignore=DL3013
RUN pip install --no-cache-dir /repo \
    && rm -fr /repo

USER backend
WORKDIR /home/backend

EXPOSE 8000
ENTRYPOINT ["acronyms", "--host", "0.0.0.0", "--port", "8000"]
