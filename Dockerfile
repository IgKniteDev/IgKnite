# SPDX-License-Identifier: MIT

# Set image version and type.
FROM python:3.12

# Copy project files and set working directory.
WORKDIR /igknite
COPY . /igknite/
RUN pip install poetry && poetry install --sync --no-root

# Set proper frontend for Debian and install external dependencies.
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y --no-install-recommends ffmpeg
RUN rm -rf /var/lib/apt/lists/*

# Real-time project view.
ENV PYTHONUNBUFFERED 1

# Run.
CMD [ "poetry", "run", "python", "main.py" ]