FROM python:3.7.3-slim-stretch

ENV PIPENV_NOSPIN 1
ENV PIPENV_VENV_IN_PROJECT 1

# Install basic packages.
RUN apt-get update \
  && apt-get upgrade -y --no-install-recommends \
  && apt-get install -y --no-install-recommends \
      curl \
  && apt-get autoremove \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install the Python shared packages.
RUN pip install --no-cache-dir --user --upgrade pip \
  && pip install --no-cache-dir --user --upgrade pipenv

# Copy the source and Pipenv files.
COPY Pipfile /
COPY Pipfile.lock /
COPY src/ /

# Install the Pipenv.
RUN python -m pipenv --clear --site-packages install --deploy \
    && rm "${WORK_DIR}/Pipfile.lock"

# Set the entrypoint.
ENTRYPOINT ["python", "-m", "pipenv", "run", "python", "app.py"]
