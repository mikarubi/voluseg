---
sidebar_label: aws
title: _tools.aws
---

## boto3

## datetime

## timezone

## JobDefinitionException Objects

```python
class JobDefinitionException(Exception)
```

#### format\_voluseg\_kwargs

```python
def format_voluseg_kwargs(voluseg_kwargs: dict) -> dict
```

#### run\_job\_in\_aws\_batch

```python
def run_job_in_aws_batch(job_name_prefix: str,
                         voluseg_kwargs: dict,
                         aws_local_profile: str = None,
                         vcpus: int = 32,
                         memory: int = 65536)
```

Submit a Voluseg job to AWS Batch.

**Arguments**

* **job_name_prefix** (`str`): Job name prefix, it will be concatenated with the current timestamp.
Example: &quot;my-voluseg-job&quot; -&gt; &quot;my-voluseg-job-2024-10-01T06-39-10Z00-00&quot;
* **voluseg_kwargs** (`dict`): Voluseg parameters.
* **aws_local_profile** (`str`): AWS profile name. Default is None.
* **vcpus** (`int`): Number of vCPUs. Default is 32.
* **memory** (`int`): Memory in MB. Default is 65536.

**Returns**

* `dict`: Dictionary with the job_name and batch_job_id.

#### export\_to\_s3

```python
def export_to_s3(local_path: str, bucket_name: str, object_name: str)
```

