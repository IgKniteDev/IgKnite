# Set image version and type.
FROM python:3.11-slim

# Copy project files and set working directory.
WORKDIR /app
COPY . /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg for music commands.
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg

# Real-time project view.
ENV PYTHONUNBUFFERED 1

# Run.
CMD [ "python", "main.py" ]