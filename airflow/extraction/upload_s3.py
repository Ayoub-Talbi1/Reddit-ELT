import pathlib
import sys
import boto3
import botocore
import configparser
from validation import validate_input

"""
Part of DAG. Take Reddit data and upload to S3 bucket. Takes one command line argument of format YYYYMMDD. 
This represents the file downloaded from Reddit, which will be in the /tmp folder.
"""

BUCKET_NAME = 'BUCKET_NAME'
AWS_REGION = 'AWS_REGION'


try:
    output_name = sys.argv[1]
except Exception as e:
    print(f"Command line argument not passed. Error {e}")
    sys.exit(1)


FILENAME = f"{output_name}.csv"
KEY = FILENAME



def main():
    """Upload input file to S3 bucket"""
    validate_input(output_name)
    client = connect_to_s3()
    upload_file_to_s3(client)


def connect_to_s3():
    """Connect to S3 Instance"""
    try:
        session = boto3.Session(
        aws_access_key_id='aws_access_key_id',
        aws_secret_access_key='aws_secret_access_key',
        region_name='region_name')
        s3_client = session.client('s3')
        return s3_client
    except Exception as e:
        print(f"Can't connect to S3. Error: {e}")
        sys.exit(1)


def upload_file_to_s3(client):
    """Upload file to S3 Bucket"""
    client.upload_file(
        Filename="/tmp/" + FILENAME, Bucket=BUCKET_NAME, Key=KEY
    )


if __name__ == "__main__":
    main()
