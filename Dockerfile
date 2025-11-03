# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create group and user 'postfix' with specific uid/gid, and add to adm group (gid 4)
RUN addgroup --gid 115 postfix \
    && adduser --uid 110 --gid 115 --disabled-password --gecos "" \
        --home "/nonexistent" --shell "/sbin/nologin" --no-create-home postfix \
    && adduser postfix adm

# Install postfix to get the postqueue binary
RUN apt-get update && apt-get install -y --no-install-recommends postfix && rm -rf /var/lib/apt/lists/*

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=src/requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the postfix user to run the application.
USER postfix

# Copy the source code into the container.
COPY src/ .

# Expose the port that the application listens on.
EXPOSE 9115

# Run the application.
ENTRYPOINT ["python", "./postfix_exporter.py"] 
