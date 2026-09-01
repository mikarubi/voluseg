FROM python:3.12.4-slim

USER root

WORKDIR /voluseg

RUN apt-get update && apt-get install -y --no-install-recommends git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Update pip
RUN python3 -m pip install --upgrade pip

# Install requirements
COPY requirements-docker.txt /voluseg/requirements-docker.txt
RUN pip install --no-cache-dir -r requirements-docker.txt

# Install voluseg
COPY src/voluseg /voluseg/src/voluseg
COPY pyproject.toml /voluseg/pyproject.toml
COPY app /voluseg/app
RUN pip install --no-cache-dir -e .

# Create directories
RUN mkdir /voluseg/data
RUN mkdir /voluseg/output
RUN mkdir /voluseg/logs

CMD ["python3", "/voluseg/app/app.py"]