FROM python:3.9.11

ARG TARGETARCH

RUN adduser backend

COPY . /repo

RUN pip install /repo \
    && rm -fr /repo

USER backend
WORKDIR /home/backend

EXPOSE 8000
ENTRYPOINT ["acronyms", "--host", "0.0.0.0", "--port", "8000"]
