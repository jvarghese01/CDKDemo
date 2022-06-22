import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_apigateway as apigateway,
                     aws_s3 as s3,
                     aws_s3_notifications,
                     aws_lambda as lambda_,
                     aws_iam as _iam, 
                     aws_dynamodb,
                     aws_sns as sns,
                     aws_sns_subscriptions as subscriptions)
                     

class CDKExampleService(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        bucket = s3.Bucket(self, "CDKExampleBucket")

        file_upload_handler = lambda_.Function(self, "CDKExample",
            function_name="CDKExample",
            runtime=lambda_.Runtime.PYTHON_3_7,
            code=lambda_.Code.from_asset("resources"),
            handler="file-fetcher.handler",
            environment=dict(
            BUCKET_NAME=bucket.bucket_name)
        )
            
        bucket.grant_read_write(file_upload_handler)

        # create dynamo table
        demo_table = aws_dynamodb.Table(
            self, "demo_table",
            partition_key=aws_dynamodb.Attribute(
                name="id",
                type=aws_dynamodb.AttributeType.STRING
            )
        )
        
                
        upload_event_topic = sns.Topic(
          self,
          id="sample_sns_topic_id"
        ) 
        
        
        file_rekognition_handler = lambda_.Function(self, "CDKRekogExample",
            function_name="CDKRekogExample",
            runtime=lambda_.Runtime.PYTHON_3_7,
            code=lambda_.Code.from_asset("resources"),
            handler="file-rekognition.handler",
            environment=dict(
            BUCKET_NAME=bucket.bucket_name, TABLE_NAME=demo_table.table_name, SNS_TOPIC_ARN=upload_event_topic.topic_arn)
        )        
        
        bucket.grant_read_write(file_rekognition_handler)
        
        notification = aws_s3_notifications.LambdaDestination(file_rekognition_handler)
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notification)
        
        lambda_rekognition_access = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            actions=["rekognition:DetectLabels", "rekognition:DetectModerationLabels"],
            resources=["*"]
        )

        file_rekognition_handler.add_to_role_policy(lambda_rekognition_access)
        

        
        demo_table.grant_read_write_data(file_rekognition_handler)
        
        api = apigateway.RestApi(self, "cdk-example-api",
                  rest_api_name="CDK Example Service",
                  description="This is a CDK Example.")
              
        get_widgets_integration = apigateway.LambdaIntegration(file_upload_handler,
            request_templates={"application/json": '{ "statusCode": "200" }'})
            
        api.root.add_method("GET", get_widgets_integration) 
        

        
        
        file_integration_handler = lambda_.Function(self, "CDKIntegrationExample",
            function_name="CDKIntegrationExample",
            runtime=lambda_.Runtime.PYTHON_3_7,
            code=lambda_.Code.from_asset("resources"),
            handler="file-integration.handler",
            environment=dict(
            BUCKET_NAME=bucket.bucket_name, TABLE_NAME=demo_table.table_name, SNS_TOPIC_ARN=upload_event_topic.topic_arn)
        ) 
        
        upload_event_topic.add_subscription(subscriptions.LambdaSubscription(file_integration_handler))
        upload_event_topic.grant_publish(file_rekognition_handler)
        
        

                
        