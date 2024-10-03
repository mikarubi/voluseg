from constructs import Construct
from aws_cdk import (
    Stack,
    Tags,
    Size,
    RemovalPolicy,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_batch as batch,
    aws_ecs as ecs,
    aws_s3 as s3,
)
import boto3


class AwsBatchStack(Stack):
    """
    References:
    - https://constructs.dev/packages/@aws-cdk/aws-batch-alpha/v/2.95.1-alpha.0?lang=python
    - https://aws.amazon.com/blogs/hpc/introducing-support-for-per-job-amazon-efs-volumes-in-aws-batch/
    - https://docs.aws.amazon.com/batch/latest/userguide/efs-volumes.html
    - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html
    - https://docs.aws.amazon.com/efs/latest/ug/accessing-fs-create-security-groups.html
    """

    def __init__(
        self,
        scope: Construct,
        stack_id: str = "VolusegBatchStack",
        ebs_volume_size: int = 3000,
        **kwargs,
    ) -> None:

        # get the default aws region
        boto_client = boto3.client("sts")
        aws_region = boto_client.meta.region_name
        print(f"Using default region: {aws_region}")

        # get the aws account id
        aws_account_id = boto_client.get_caller_identity()["Account"]
        print(f"Using account id: {aws_account_id}")
        super().__init__(
            scope,
            stack_id,
            env={"region": aws_region, "account": aws_account_id},
            **kwargs,
        )

        batch_service_role_id = f"{stack_id}-BatchServiceRole"
        ecs_instance_role_id = f"{stack_id}-EcsInstanceRole"
        batch_jobs_access_role_id = f"{stack_id}-BatchJobsAccessRole"
        vpc_id = f"{stack_id}-Vpc"
        security_group_id = f"{stack_id}-SecurityGroup"
        launch_template_id = f"{stack_id}-LaunchTemplate"
        compute_env_id = f"{stack_id}-compute-env"
        job_queue_id = f"{stack_id}-job-queue"
        job_definition_id = f"{stack_id}-job-definition"
        tag_key_name = stack_id

        # AWS Batch service role
        batch_service_role = iam.Role(
            scope=self,
            id=batch_service_role_id,
            assumed_by=iam.ServicePrincipal("batch.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSBatchServiceRole"
                )
            ],
        )
        Tags.of(batch_service_role).add(tag_key_name, f"{stack_id}-BatchServiceRole")

        # ECS instance role
        ecs_instance_role = iam.Role(
            scope=self,
            id=ecs_instance_role_id,
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonEC2ContainerServiceforEC2Role"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "CloudWatchLogsFullAccess"
                ),
            ],
        )
        Tags.of(ecs_instance_role).add(tag_key_name, f"{stack_id}-EcsInstanceRole")

        # Batch jobs access role
        batch_jobs_access_role = iam.Role(
            scope=self,
            id=batch_jobs_access_role_id,
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEC2ContainerRegistryFullAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "CloudWatchLogsFullAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonEFSCSIDriverPolicy"
                ),
            ],
        )
        Tags.of(batch_jobs_access_role).add(
            tag_key_name, f"{stack_id}-BatchJobsAccessRole"
        )

        # VPC
        vpc = ec2.Vpc(
            scope=self,
            id=vpc_id,
            max_azs=3,  # Default is all AZs in the region
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
                ),
            ],
        )

        # Security Group
        security_group = ec2.SecurityGroup(
            scope=self,
            id=security_group_id,
            vpc=vpc,
            description="Security group for Voluseg Batch Stack",
            allow_all_outbound=True,
        )
        # Add inbound rules to the security group as required
        # For example, to allow SSH access (not recommended for production)
        # security_group.add_ingress_rule(
        #     peer=ec2.Peer.any_ipv4(),
        #     connection=ec2.Port.tcp(22),
        #     description="Allow SSH access from anywhere"
        # )

        # Define the block device
        block_device_2T = ec2.BlockDevice(
            device_name="/dev/xvda",
            volume=ec2.BlockDeviceVolume.ebs(
                volume_size=ebs_volume_size, delete_on_termination=True
            ),
        )

        # Launch templates
        multipart_user_data = ec2.MultipartUserData()
        commands_user_data = ec2.UserData.for_linux()
        multipart_user_data.add_user_data_part(
            commands_user_data, ec2.MultipartBody.SHELL_SCRIPT, True
        )
        multipart_user_data.add_commands("mkfs -t ext4 /dev/xvda")
        multipart_user_data.add_commands("mkdir -p /tmp")
        multipart_user_data.add_commands("mount /dev/xvda /tmp")

        launch_template = ec2.LaunchTemplate(
            scope=self,
            id=launch_template_id,
            launch_template_name=launch_template_id,
            block_devices=[block_device_2T],
            machine_image=ec2.MachineImage.generic_linux(ami_map=ami_map),
            ebs_optimized=True,
            user_data=multipart_user_data,
        )
        Tags.of(launch_template).add("AWSBatchService", "batch")

        # Compute environment
        ecs_machine_image = batch.EcsMachineImage(
            image=ec2.MachineImage.generic_linux(ami_map=ami_map),
            image_type=batch.EcsMachineImageType.ECS_AL2,
        )
        compute_env = batch.ManagedEc2EcsComputeEnvironment(
            scope=self,
            id=compute_env_id,
            vpc=vpc,
            instance_types=[ec2.InstanceType("optimal")],
            images=[ecs_machine_image],
            maxv_cpus=128,
            minv_cpus=0,
            security_groups=[security_group],
            service_role=batch_service_role,  # type: ignore because Role implements IRole
            instance_role=ecs_instance_role,  # type: ignore because Role implements IRole
            launch_template=launch_template,
        )
        Tags.of(compute_env).add(tag_key_name, f"{stack_id}-compute-env")

        # Job queue
        job_queue = batch.JobQueue(
            scope=self,
            id=job_queue_id,
            job_queue_name=job_queue_id,
            priority=1,
            compute_environments=[
                batch.OrderedComputeEnvironment(
                    compute_environment=compute_env, order=1
                )
            ],
        )
        Tags.of(job_queue).add(tag_key_name, f"{stack_id}-job-queue")

        # Batch job definition
        docker_image = ecs.ContainerImage.from_registry(
            "ghcr.io/mikarubi/voluseg/voluseg:latest"
        )
        job_definition = batch.EcsJobDefinition(
            scope=self,
            id=job_definition_id,
            job_definition_name=job_definition_id,
            propagate_tags=True,
            container=batch.EcsEc2ContainerDefinition(
                scope=self,
                id=job_definition_id + "-container",
                image=docker_image,
                cpu=32,
                memory=Size.gibibytes(64),  # Memory 64 GB
                job_role=batch_jobs_access_role,
                volumes=[
                    batch.EcsVolume.host(
                        host_path="/tmp",
                        container_path="/tmp/voluseg_output",
                        name=f"{stack_id}-volume",
                        readonly=False,
                    )
                ],
            ),
            retry_attempts=1,
        )
        Tags.of(job_definition).add(tag_key_name, f"{stack_id}-job-definition")

        # S3 bucket
        s3_bucket = s3.Bucket(
            scope=self,
            id=f"{stack_id}-Bucket",
            bucket_name=f"{stack_id.lower()}-bucket",
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Add S3 permissions to the batch jobs access role
        batch_jobs_access_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:ListBucket",
                    "s3:DeleteObject",
                ],
                resources=[s3_bucket.bucket_arn, f"{s3_bucket.bucket_arn}/*"],
            )
        )


ami_map = {
    "ap-south-1": "ami-0ac26d07e5b3dee2c",
    "ap-southeast-1": "ami-04c2b121d2518d721",
    "ap-southeast-2": "ami-0a6407061c6f43c25",
    "ap-northeast-1": "ami-0a50b50d3f0255ea3",
    "ap-northeast-2": "ami-03c5f630f6d2dd64b",
    "ca-central-1": "ami-0f573ab699762ead1",
    "eu-west-1": "ami-08452023a2c1a3bac",
    "eu-west-2": "ami-0f3246ed2fef95399",
    "eu-west-3": "ami-06dc37dc7de5f33d0",
    "eu-north-1": "ami-00dc593afd34193fc",
    "eu-central-1": "ami-04fc217f16fc2aceb",
    "sa-east-1": "ami-00c6fb0d796b16790",
    "us-east-1": "ami-014ff0fa8ac643097",
    "us-east-2": "ami-01fb8a683bddd95be",
    "us-west-1": "ami-0389998efa11239f6",
    "us-west-2": "ami-026b024d2182d335f",
}
