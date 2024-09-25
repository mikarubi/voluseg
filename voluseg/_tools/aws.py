import boto3


class JobDefinitionException(Exception):
    pass


def run_job_in_aws_batch(
    job_id: str,
    job_private_key: str,
    command: str,
):
    client = boto3.client('batch')

    stack_id = "VolusegBatchStack"
    aws_batch_job_definition = f"{stack_id}-job-definition"
    aws_batch_job_queue = f'{stack_id}-job-queue'
    job_name = f'voluseg-job-{job_id}'

    job_def_resp = client.describe_job_definitions(jobDefinitionName=aws_batch_job_definition)
    job_defs = job_def_resp['jobDefinitions']
    if len(job_defs) == 0:
        raise JobDefinitionException(f'Job definition not found: {aws_batch_job_definition}')

    env_vars = {
        'JOB_ID': job_id,
        'JOB_PRIVATE_KEY': job_private_key,
        'APP_EXECUTABLE': command,
        'VOLUSEG_JOB_WORKING_DIR': '/tmp/voluseg-jobs',
    }

    response = client.submit_job(
        jobName=job_name,
        jobQueue=aws_batch_job_queue,
        jobDefinition=aws_batch_job_definition,
        containerOverrides={
            'environment': [
                {
                    'name': k,
                    'value': v
                }
                for k, v in env_vars.items()
            ],
        },
    )

    batch_job_id = response['jobId']
    print(f'AWS Batch job submitted: {job_id} {batch_job_id}')
