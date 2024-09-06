# Voluseg container

Build the image locally:
```bash
DOCKER_BUILDKIT=1 docker build -t voluseg .
```

Or pull the image from GHCR:
```bash
docker pull ghcr.io/mikarubi/voluseg/voluseg:latest
```

Run with local data volume mount, default parameters values and hot reload for the voluseg package:
```bash
docker run \
-v $(pwd)/sample_data:/voluseg/data \
-v $(pwd)/output:/voluseg/output \
-v $(pwd)/voluseg:/voluseg/voluseg \
-v $(pwd)/app:/voluseg/app \
voluseg
```

Run with local data volume mount and user-defined parameters values:
```bash
docker run \
-v $(pwd)/sample_data:/voluseg/data \
-v $(pwd)/output:/voluseg/output \
voluseg \
python3 /voluseg/app/app.py \
--registration high \
--diam-cell 5.0
```