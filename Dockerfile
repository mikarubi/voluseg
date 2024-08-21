FROM apache/spark-py:v3.4.0

USER root

WORKDIR /voluseg

RUN apt-get update && apt-get install -y wget unzip && \
    apt-get update && apt-get install -y git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

# Download and install ANTs
RUN wget https://github.com/ANTsX/ANTs/releases/download/v2.5.3/ants-2.5.3-ubuntu-20.04-X64-gcc.zip
RUN unzip ants-2.5.3-ubuntu-20.04-X64-gcc.zip -d /
RUN rm ants-2.5.3-ubuntu-20.04-X64-gcc.zip

# Install requirements
COPY requirements-docker.txt /voluseg/requirements-docker.txt
RUN pip install --no-cache-dir -r requirements-docker.txt

# Install voluseg
COPY README.md /voluseg/README.md
COPY setup.py /voluseg/setup.py
COPY voluseg /voluseg/voluseg
COPY app /voluseg/app
RUN pip install --no-cache-dir -e .

# Create directories
RUN mkdir /voluseg/data
RUN mkdir /voluseg/output
RUN mkdir /voluseg/logs

# EXPOSE 80

CMD ["python3", "/voluseg/app/app.py"]