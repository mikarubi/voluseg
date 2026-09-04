# Dask Configuration for voluseg

This document describes how to configure Dask distributed computing in the voluseg pipeline for optimal performance.

## Overview

The voluseg pipeline uses Dask for parallel processing of volumetric data. By default, it uses a simple local cluster, but you can configure it for better performance or to use cluster resources.

## Quick Start

### 1. Basic Configuration

```python
import voluseg

# Configure Dask with custom settings
parameters = voluseg.load_parameters('parameters.json')
parameters['dask_config'] = {
    'n_workers': 4,
    'n_cores_per_worker': 2,
    'memory_limit': '4GB',
    'cluster_type': 'local'
}

# Configure Dask
client = voluseg.configure_dask_from_parameters(parameters)

# Run pipeline
voluseg.step1_process_volumes(parameters)
```

### 2. Using YAML Configuration

Create a configuration file `dask_config.yaml`:

```yaml
n_workers: 4
n_cores_per_worker: 2
memory_limit: "4GB"
cluster_type: "local"
dashboard_address: "localhost"
dashboard_port: 8787
```

Then use it:

```python
parameters['dask_config'] = {'config_file': 'dask_config.yaml'}
client = voluseg.configure_dask_from_parameters(parameters)
```

### 3. Command Line Interface

```bash
# Use environment variables
export VOLUSEG_DASK_N_WORKERS=4
export VOLUSEG_DASK_MEMORY_LIMIT="4GB"
python -m app.app run-pipeline

# Or use command line options
python -m app.app run-pipeline --dask-n-workers 4 --dask-memory-limit "4GB"
```

## Configuration Options

### Basic Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `n_workers` | int | CPU count | Number of workers |
| `n_cores_per_worker` | int | 1 | Cores per worker |
| `memory_limit` | str | "2GB" | Memory limit per worker |
| `threads_per_worker` | int | n_cores_per_worker | Threads per worker |
| `cluster_type` | str | "local" | Cluster type |

### Cluster Types

#### Local Cluster
```yaml
cluster_type: "local"
cluster_config:
  local_directory: "/tmp/dask-worker-space"
```

#### SLURM Cluster
```yaml
cluster_type: "slurm"
cluster_config:
  queue: "normal"
  project: "your_project"
  walltime: "02:00:00"
  local_directory: "/tmp/dask-worker-space"
  log_directory: "/tmp/dask-logs"
```

#### PBS Cluster
```yaml
cluster_type: "pbs"
cluster_config:
  queue: "normal"
  project: "your_project"
  walltime: "02:00:00"
  local_directory: "/tmp/dask-worker-space"
  log_directory: "/tmp/dask-logs"
```

#### SGE Cluster
```yaml
cluster_type: "sge"
cluster_config:
  queue: "all.q"
  project: "your_project"
  walltime: "02:00:00"
  local_directory: "/tmp/dask-worker-space"
  log_directory: "/tmp/dask-logs"
```

### Dashboard Configuration

```yaml
dashboard_address: "localhost"
dashboard_port: 8787
```

## Monitoring

### Dashboard
Once Dask is configured, you can access the dashboard at:
```
http://localhost:8787
```

### Check Configuration
```python
import voluseg
voluseg.print_dask_info()
```

## Best Practices

### 1. Memory Management
- Set `memory_limit` based on your data size
- Monitor memory usage in the dashboard
- Use `distributed.worker.memory.target` for fine-tuning

### 2. Worker Configuration
- For CPU-intensive tasks: `n_cores_per_worker = 1`
- For I/O-intensive tasks: `n_cores_per_worker > 1`
- Balance workers vs cores per worker

### 3. Cluster Selection
- **Local**: Good for development and small datasets
- **SLURM/PBS/SGE**: For HPC environments with large datasets

### 4. Performance Tuning
```python
# For large datasets
parameters['dask_config'] = {
    'n_workers': 8,
    'n_cores_per_worker': 1,
    'memory_limit': '8GB',
    'cluster_type': 'local'
}

# For memory-intensive tasks
parameters['dask_config'] = {
    'n_workers': 4,
    'n_cores_per_worker': 2,
    'memory_limit': '16GB',
    'cluster_type': 'local'
}
```

### Debugging
```python
# Get detailed configuration info
config_info = client.get_config_info()
print(config_info)

# Check worker status
print(client.scheduler_info()['workers'])
```

## Examples

### Example 1: Local Development
```python
import voluseg

# Simple local configuration
parameters = voluseg.load_parameters('parameters.json')
parameters['dask_config'] = {
    'n_workers': 2,
    'memory_limit': '4GB'
}

client = voluseg.configure_dask_from_parameters(parameters)
```

### Example 2: HPC Environment
```python
import voluseg

# SLURM configuration
parameters = voluseg.load_parameters('parameters.json')
parameters['dask_config'] = {
    'n_workers': 16,
    'n_cores_per_worker': 4,
    'memory_limit': '32GB',
    'cluster_type': 'slurm',
    'cluster_config': {
        'queue': 'normal',
        'project': 'my_project',
        'walltime': '04:00:00'
    }
}

client = voluseg.configure_dask_from_parameters(parameters)
```

### Example 3: YAML Configuration
```yaml
# dask_config.yaml
n_workers: 8
n_cores_per_worker: 2
memory_limit: "8GB"
cluster_type: "local"
dashboard_address: "0.0.0.0"
dashboard_port: 8787
cluster_config:
  local_directory: "/scratch/dask-worker-space"
```

```python
import voluseg

parameters = voluseg.load_parameters('parameters.json')
parameters['dask_config'] = {'config_file': 'dask_config.yaml'}
client = voluseg.configure_dask_from_parameters(parameters)
```

