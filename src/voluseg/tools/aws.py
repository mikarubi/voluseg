import boto3
from datetime import datetime, timezone


class JobDefinitionException(Exception):
    pass


def format_voluseg_kwargs(voluseg_kwargs: dict) -> dict:
    parameter_to_env_var = {
        "detrending": "VOLUSEG_DETRENDING",
        "registration": "VOLUSEG_REGISTRATION",
        "registration_restrict": "VOLUSEG_REGISTRATION_RESTRICT",
        "diam_cell": "VOLUSEG_DIAM_CELL",
        "ds": "VOLUSEG_DS",
        "planes_pad": "VOLUSEG_PLANES_PAD",
        "planes_packed": "VOLUSEG_PLANES_PACKED",
        "parallel_clean": "VOLUSEG_PARALLEL_CLEAN",
        "parallel_volume": "VOLUSEG_PARALLEL_VOLUME",
        "save_volume": "VOLUSEG_SAVE_VOLUME",
        "type_timepoints": "VOLUSEG_TYPE_TIMEPOINTS",
        "type_mask": "VOLUSEG_TYPE_MASK",
        "timepoints": "VOLUSEG_TIMEPOINTS",
        "f_hipass": "VOLUSEG_F_HIPASS",
        "f_volume": "VOLUSEG_F_VOLUME",
        "n_cells_block": "VOLUSEG_N_CELLS_BLOCK",
        "n_colors": "VOLUSEG_N_COLORS",
        "res_x": "VOLUSEG_RES_X",
        "res_y": "VOLUSEG_RES_Y",
        "res_z": "VOLUSEG_RES_Z",
        "t_baseline": "VOLUSEG_T_BASELINE",
        "t_section": "VOLUSEG_T_SECTION",
        "thr_mask": "VOLUSEG_THR_MASK",
        "dir_input": "VOLUSEG_DIR_INPUT",
        "dir_output": "VOLUSEG_DIR_OUTPUT",
    }
    formatted_kwargs = {
        parameter_to_env_var[key]: str(value)
        for key, value in voluseg_kwargs.items()
        if key in parameter_to_env_var
    }
    return formatted_kwargs


def run_job_in_aws_batch(
    job_name_prefix: str,
    voluseg_kwargs: dict,
    aws_local_profile: str = None,
    vcpus: int = 32,
    memory: int = 65536,
):
    """
    Submit a Voluseg job to AWS Batch.

    Parameters
    ----------
    job_name_prefix : str
        Job name prefix, it will be concatenated with the current timestamp.
        Example: "my-voluseg-job" -> "my-voluseg-job-2024-10-01T06-39-10Z00-00"
    voluseg_kwargs : dict
        Voluseg parameters.
    aws_local_profile : str
        AWS profile name. Default is None.
    vcpus : int
        Number of vCPUs. Default is 32.
    memory : int
        Memory in MB. Default is 65536.

    Returns
    -------
    dict
        Dictionary with the job_name and batch_job_id.
    """
    if aws_local_profile is None:
        session = boto3.Session()
    else:
        session = boto3.Session(profile_name=aws_local_profile)
    client = session.client("batch")

    stack_id = "VolusegBatchStack"
    aws_batch_job_definition = f"{stack_id}-job-definition"
    aws_batch_job_queue = f"{stack_id}-job-queue"

    iso_string = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace(":", "-")
        .replace("+", "Z")
    )
    job_name = f"{job_name_prefix}-{iso_string}"

    job_def_resp = client.describe_job_definitions(
        jobDefinitionName=aws_batch_job_definition
    )
    job_defs = job_def_resp["jobDefinitions"]
    if len(job_defs) == 0:
        raise JobDefinitionException(
            f"Job definition not found: {aws_batch_job_definition}"
        )

    env_vars = format_voluseg_kwargs(voluseg_kwargs)
    env_vars["VOLUSEG_DIR_OUTPUT"] = "/tmp/voluseg-jobs"
    env_vars["VOLUSEG_JOB_ID"] = job_name

    response = client.submit_job(
        jobName=job_name,
        jobQueue=aws_batch_job_queue,
        jobDefinition=aws_batch_job_definition,
        containerOverrides={
            "environment": [{"name": k, "value": v} for k, v in env_vars.items()],
            "resourceRequirements": [
                {"type": "MEMORY", "value": str(memory)},
                {"type": "VCPU", "value": str(vcpus)},
            ],
        },
    )
    batch_job_id = response["jobId"]
    print(f"AWS Batch job submitted: {job_name} {batch_job_id}")
    return {
        "job_name": job_name,
        "batch_job_id": batch_job_id,
    }


def export_to_s3(
    local_path: str,
    bucket_name: str,
    object_name: str,
):
    s3 = boto3.client("s3")
    s3.upload_file(
        Filename=local_path,
        Bucket=bucket_name,
        Key=object_name,
    )
    print(f"File uploaded to s3://{bucket_name}/{object_name}")
