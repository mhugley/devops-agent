from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_cloudwatch as cloudwatch,
    RemovalPolicy,
    Duration
)
from constructs import Construct

class DevopsLabStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Target Bucket
        bucket = s3.Bucket(self, "HeartbeatBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # 2. The Microservice (Lambda)
        heartbeat_func = _lambda.Function(self, "HeartbeatFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                'BUCKET_NAME': bucket.bucket_name
            }
        )

        # 3. Permissions (The line you will comment out later to 'break' the app)
        bucket.grant_write(heartbeat_func)

        # 4. CloudWatch Alarm (The trigger for the DevOps Agent)
        error_metric = heartbeat_func.metric_errors(period=Duration.minutes(1))
        
        cloudwatch.Alarm(self, "LambdaErrorAlarm",
            metric=error_metric,
            threshold=1,
            evaluation_periods=1,
            alarm_description="DevOps Agent: Please investigate why the Heartbeat Lambda is failing."
        )