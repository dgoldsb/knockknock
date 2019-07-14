FROM python:3.7.3-slim-stretch

ENV PIPENV_NOSPIN 1
ENV PIPENV_VENV_IN_PROJECT 1

# Install basic packages.
RUN apt-get update \
  && apt-get upgrade -y --no-install-recommends \
  && apt-get install -y --no-install-recommends \
      curl \
      cron \
  && apt-get autoremove \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install the Python shared packages.
RUN pip install --no-cache-dir --user --upgrade pip \
  && pip install --no-cache-dir --user --upgrade pipenv

# Copy the source and Pipenv files.
COPY Pipfile /
COPY Pipfile.lock /
COPY cron-schedule /
COPY src/ /

# Install the Pipenv.
RUN python -m pipenv --clear --site-packages install --deploy \
    && rm "${WORK_DIR}/Pipfile.lock"

# Copy cron-nmap file to the cron.d directory
COPY cron-schedule /etc/cron.d/cron-schedule

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cron-schedule

# Apply cron job
RUN crontab /etc/cron.d/cron-schedule

# Run the command on container startup
CMD ["cron", "-f"]
