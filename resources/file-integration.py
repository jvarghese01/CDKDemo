import boto3
import logging
from botocore.exceptions import ClientError
from urllib.request import urlopen
import os

def handler(event, context):
    
    print(event)