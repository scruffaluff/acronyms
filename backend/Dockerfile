FROM python:3.9.11

ARG TARGETARCH

RUN adduser backend

COPY . /repo

RUN pip install /repo \
    && rm -fr /repo

# Set Bash as default shell.
SHELL ["/bin/bash", "-c"]

# Required on ARM images due to psycopg2-binary bug.
RUN if [[ "$TARGETARCH" == "arm64" ]]; then \
        pip uninstall psycopg2-binary && pip install psycopg2==2.9.3; \
    fi

USER backend
WORKDIR /home/backend

EXPOSE 8000
ENTRYPOINT ["acronyms", "--host", "0.0.0.0", "--port", "8000"]
