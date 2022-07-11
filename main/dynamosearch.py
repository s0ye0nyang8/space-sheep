from botocore.exceptions import ClientError
from django.contrib import messages
import hashlib
import uuid
import boto3

def searchUser(email,password):
    
