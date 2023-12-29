import os

import boto3
from botocore.client import Config
from botocore.exceptions import NoCredentialsError, ClientError

from mediafetchxpress.settings import S3_ACCESS_KEY, S3_URL, S3_SECRET_KEY

minio_client = boto3.client('s3',
                            endpoint_url=S3_URL,
                            aws_access_key_id=S3_ACCESS_KEY,
                            aws_secret_access_key=S3_SECRET_KEY,
                            config=Config(signature_version='s3v4'),
                            region_name='us-east-1')


def upload_downloaded_file_to_s3(file_path, bucket_name):
    """
    Uploads the downloaded file to an S3 bucket.
    If the bucket doesn't exist, it creates a new bucket.
    """
    try:
        if not s3_bucket_exists(minio_client, bucket_name):
            minio_client.create_bucket(Bucket=bucket_name)

        file_name = os.path.basename(file_path)
        minio_client.upload_file(file_path, bucket_name, file_name)
        print(f"File uploaded to S3: s3://{bucket_name}/{file_name}")

    except NoCredentialsError:
        print("Credentials not available")
    except ClientError as e:
        print(f"An error occurred: {e}")


def s3_bucket_exists(s3_client, bucket_name):
    """
    Check if an S3 bucket exists
    """
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError:
        return False
