FROM python:3.9-slim-buster

RUN apt-get update && \
    apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy the crontab file into the container
COPY crontab /etc/cron.d/crontab

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/crontab

# Apply the cron job
RUN crontab /etc/cron.d/crontab

# Run the command on container startup
CMD ["/bin/bash", "-c", "source /app/venv/bin/activate && cron && python main.py"]
