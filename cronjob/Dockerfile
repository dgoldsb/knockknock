FROM alpine:3.10

# Install packages and install Ruby Gems.
RUN apk add --no-cache \
    bash \
    curl \
    nmap

# Copy over the file.
COPY cron-nmap /
COPY report_nmap.sh /

# Set script permissions.
RUN chmod +x "/report_nmap.sh"

# Copy cron-nmap file to the cron.d directory
COPY cron-nmap /etc/cron.d/cron-nmap

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cron-nmap

# Apply cron job
RUN crontab /etc/cron.d/cron-nmap

# Run the command on container startup
CMD ["crond", "-f"]
