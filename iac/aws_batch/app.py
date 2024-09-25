#!/usr/bin/env python3
import aws_cdk as cdk

from aws_batch.aws_batch_stack import AwsBatchStack


# --------------------------------------------------------------
# User defined values
# --------------------------------------------------------------
stack_id = "VolusegBatchStack"
ebs_volume_size = 3000

# --------------------------------------------------------------
# --------------------------------------------------------------

app = cdk.App()

AwsBatchStack(
    scope=app,
    stack_id=stack_id,
    ebs_volume_size=ebs_volume_size,
)

app.synth()
