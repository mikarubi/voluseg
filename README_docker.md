# Voluseg container

Build the image:
```bash
DOCKER_BUILDKIT=1 docker build -t voluseg .
```

Run with local data volume mount:
```bash
docker run -v $(pwd)/data:/voluseg/data voluseg
```

Run with local data volume mount and hot reload for the voluseg package:
```bash
docker run \
-v $(pwd)/data:/voluseg/data \
-v $(pwd)/output:/voluseg/output \
-v $(pwd)/voluseg:/voluseg/voluseg \
-v $(pwd)/app:/voluseg/app \
voluseg
```