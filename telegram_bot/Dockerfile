# Use an official Python runtime as a parent image
FROM python:3.11-slim
COPY --from=docker:20.10 /usr/local/bin/docker /usr/local/bin/
RUN pip install --no-cache-dir python-telegram-bot python-telegram-bot[job-queue] requests cryptography

# Set the working directory in the container
WORKDIR /usr/src/app



