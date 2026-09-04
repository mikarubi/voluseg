FROM python:3.12.4-slim

USER root

WORKDIR /voluseg

RUN apt-get update && apt-get install -y --no-install-recommends wget unzip git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Update pip
RUN python3 -m pip install --upgrade pip

# Download and install ANTs
RUN wget https://github.com/ANTsX/ANTs/releases/download/v2.5.3/ants-2.5.3-ubuntu-20.04-X64-gcc.zip
RUN unzip ants-2.5.3-ubuntu-20.04-X64-gcc.zip -d /
RUN rm ants-2.5.3-ubuntu-20.04-X64-gcc.zip

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