import boto3
import logging
from botocore.exceptions import ClientError
from urllib.request import urlopen
import os
import json


s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')
dynamodb = boto3.client('dynamodb')
sns = boto3.client('sns')

def handler(event, context):
    
    bucket_name = (os.environ['BUCKET_NAME'])
    key = event['Records'][0]['s3']['object']['key']
    
    image = {
        'S3Object': {
            'Bucket': bucket_name,
            'Name': key
            }
        }
    
    detected_labels = rekognition_client.detect_labels(Image=image, MaxLabels=20, MinConfidence=85)

    db_result = []
    db_labels = detected_labels["Labels"]
    for label in db_labels:
        db_result.append(label["Name"])
        
    dynamodb.put_item(TableName=(os.environ['TABLE_NAME']),
        Item = {
            'id':{'S': key},
            'labels':{'S': str(db_result)}
       }
    ) 
    
    Message = {
        'id':{'S': key},
        'labels':{'S': str(db_result)}
   }
  
    
    sns.publish(TopicArn=os.environ['SNS_TOPIC_ARN'],MessageStructure='string', Message=json.dumps(Message))
    
    return{
        'statusCode': 200,
        'body': event
    }