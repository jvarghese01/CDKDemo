import boto3
import logging
from botocore.exceptions import ClientError
from urllib.request import urlopen
import os

def handler(event, context):
    


    # Upload the file
    s3_client = boto3.client('s3')
    
    try:
        
        url = event["queryStringParameters"]['url']
        name = event["queryStringParameters"]['name']
        
        with urlopen( url ) as file:
            uploadresponse = s3_client.upload_fileobj(file, os.environ['BUCKET_NAME'], name)

        return {
            'statusCode': 200,
            'body': "file uploaded to S3: " + name 
        }
        
    except ClientError as e:
        logging.error(e)
        return {
            'statusCode': 500,
            'body': "file NOT uploaded to S3: " 

        }