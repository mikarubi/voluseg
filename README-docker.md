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
-v $(pwd)/sample_data:/voluseg/data \
-v $(pwd)/output:/voluseg/output \
-v $(pwd)/voluseg:/voluseg/voluseg \
-v $(pwd)/app:/voluseg/app \
voluseg
```

docker run \
-v /mnt/shared_storage/taufferconsulting/client_catalystneuro/project_voluseg/sample_data:/voluseg/data \
-v $(pwd)/output:/voluseg/output \
-v $(pwd)/voluseg:/voluseg/voluseg \
-v $(pwd)/app:/voluseg/app \
voluseg