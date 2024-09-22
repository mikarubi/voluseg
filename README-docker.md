# Voluseg container

Pull the image from GHCR:
```bash
docker pull ghcr.io/mikarubi/voluseg/voluseg:latest
```

Run with access to your local data and pass user-defined parameters values:
```bash
docker run \
-v $(pwd)/local_data:/voluseg/data \
-v $(pwd)/output:/voluseg/output \
voluseg \
python3 /voluseg/app/app.py \
--registration high \
--diam-cell 5.0
```

## For developers

Build the image locally:
```bash
DOCKER_BUILDKIT=1 docker build -t voluseg .
```

Run with local data volume mount, default parameters values and hot reload for the voluseg package (useful for development):
```bash
docker run \
-v $(pwd)/local_data:/voluseg/data \
-v $(pwd)/output:/voluseg/output \
-v $(pwd)/voluseg:/voluseg/voluseg \
-v $(pwd)/app:/voluseg/app \
voluseg
```

## Apptainer

Pull the image from GHCR:
```bash
apptainer pull docker://ghcr.io/mikarubi/voluseg/voluseg:latest
```

Run with access to your local data and pass user-defined parameters values:
```bash
apptainer exec \
--bind $(pwd)/local_data:/voluseg/data \
--bind $(pwd)/output:/voluseg/output  \
voluseg_latest.sif \
python3 /voluseg/app/app.py \
--registration high \
--diam-cell 5.0 \
--no-parallel-volume \
--no-parallel-clean \
2>&1 | tee log_file.log
```

Run for a remote NWB file:
```bash
apptainer exec \
--bind $(pwd)/output_stream:/voluseg/output  \
voluseg_nwb-ingestion.sif \
python3 /voluseg/app/app.py \
--registration high \
--diam-cell 5.0 \
--no-parallel-volume \
--no-parallel-clean \
--dir-input "https://dandiarchive.s3.amazonaws.com/blobs/057/ecb/057ecbef-e732-4e94-8d99-40ebb74d346e" \
2>&1 | tee log_file.log
```