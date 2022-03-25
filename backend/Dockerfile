FROM python:3.9.11

RUN adduser server

COPY . /repo

RUN pip install /repo \
    && rm -fr /repo

USER server
WORKDIR /home/server

ENTRYPOINT ["acronyms", "--host", "0.0.0.0", "--port", "8000"]
