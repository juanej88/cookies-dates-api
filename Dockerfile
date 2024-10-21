# Set the python version as a build-time argument
# with Python 3.12 as the default
ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

# Create a virtual environment
RUN python -m venv /opt/venv

# Set the virtual environment as the current location
ENV PATH=/opt/venv/bin:$PATH

# Upgrade pip
RUN pip install --upgrade pip

# Set Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install os dependencies for the mini vm
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    # for mysql
    default-libmysqlclient-dev \
    pkg-config \
    # Install cron
    cron && \
    # other
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create the mini vm's code directory
RUN mkdir -p /code

# Set the working directory to that same code directory
WORKDIR /code

# Copy all files from the current directory (host) to /code in the container
COPY . /code

# Copy the requirements file into the container
COPY requirements.txt /tmp/requirements.txt

# Install the Python project requirements
RUN pip install -r /tmp/requirements.txt

# Set the Django default project name
ARG PROJ_NAME="cookiesdates"

# Create a bash script to run the Django project
# this script will execute at runtime when
# the container starts and the database is available
RUN printf "#!/bin/bash\n" > ./paracord_runner.sh && \
    printf "RUN_PORT=\"\${PORT:-8000}\"\n\n" >> ./paracord_runner.sh && \
    printf "python manage.py migrate --no-input\n" >> ./paracord_runner.sh && \
    printf "gunicorn ${PROJ_NAME}.wsgi:application --bind \"0.0.0.0:\$RUN_PORT\" &\n" >> ./paracord_runner.sh && \
    printf "cron\n" >> ./paracord_runner.sh # Start cron in the background

# Add the cron job to run every 2 hours
RUN echo "0 */2 * * * cd /code && /opt/venv/bin/python manage.py run_tasks >> /var/log/cron.log 2>&1" >> /etc/cron.d/django_cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/django_cron

# Apply the cron job
RUN crontab /etc/cron.d/django_cron

# make the bash script executable
RUN chmod +x paracord_runner.sh

# Clean up apt cache to reduce image size
RUN apt-get remove --purge -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Run the Django project via the runtime script
# when the container starts
CMD ["/bin/bash", "./paracord_runner.sh"]