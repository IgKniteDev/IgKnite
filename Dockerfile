# Initialize Python 3.10 and set current directory.
FROM python:3.10
WORKDIR /app

# Install the required Python packages.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install ffmpeg for music commands.
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg

# Copy project files to working directory.
COPY . .

# Real-time project view.
ENV PYTHONUNBUFFERED 1

# Run.
CMD [ "python", "main.py" ]