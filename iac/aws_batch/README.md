# Voluseg on AWS Batch (CDK)

This directory contains an [AWS CDK](https://docs.aws.amazon.com/cdk/) app that
provisions the infrastructure needed to run Voluseg jobs on AWS Batch: IAM
roles, a VPC and security group, an EC2 launch template with a large EBS
volume, a managed compute environment, a job queue, a job definition that runs
the `ghcr.io/mikarubi/voluseg/voluseg:latest` image, and an S3 bucket for
results.

Full setup instructions live in the documentation:
[Running on AWS Batch](https://mikarubi.github.io/voluseg/docs/getting_started/iac_aws_batch).

Quick start:

```bash
cd iac/aws_batch
pip install -r requirements.txt
cdk bootstrap   # first time only
cdk deploy
```

Submit jobs from Python with `voluseg._tools.aws.run_job_in_aws_batch`.
