# Initialize Python 3.10 and set current directory.
FROM python:3.10

# Copy project files and 
COPY . /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg for music commands.
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg

# Real-time project view.
ENV PYTHONUNBUFFERED 1

# Run.
CMD [ "python", "main.py" ]