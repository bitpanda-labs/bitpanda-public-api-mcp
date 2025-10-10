# pure python3.11 image + bitpanda certificates installed
FROM public.ecr.aws/docker/library/python:3.11-slim-bookworm

ARG USER_NAME="bp_mcp"
ARG USER_HOME="/usr/src/app"
ARG USER_ID=1000

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_INSTALLER_MODERN_INSTALLATION=0 \
    POETRY_NO_INTERACTION=1 \
    POETRY_NO_ANSI=1 \
    POETRY_HOME=/opt/poetry

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl vim git wait-for-it && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR ${USER_HOME}

RUN groupadd -g ${USER_ID} ${USER_NAME} && \
    useradd -l -u ${USER_ID} -g ${USER_ID} --create-home --home-dir ${USER_HOME} --shell /bin/bash ${USER_NAME}

COPY --chown=${USER_NAME}:${USER_NAME} poetry.lock pyproject.toml *.whl ./

RUN pip install poetry==1.8.4 \
    && poetry install --no-interaction --no-ansi --no-root

ENV PATH ${USER_HOME}/.venv/bin:${PATH}

COPY --chown=${USER_NAME}:${USER_NAME} . ./

EXPOSE 8000

USER ${USER_NAME}

# Run the application
ENTRYPOINT [ "ci/docker/entrypoint.sh" ]
CMD ["api"]
