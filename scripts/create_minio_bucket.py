#!/usr/bin/env python3
"""Script to create MinIO bucket for Foodgram static files."""

import boto3
from botocore.exceptions import ClientError
import sys


def create_minio_bucket():
    """Create foodgram bucket in MinIO."""
    try:
        # MinIO connection settings
        s3_client = boto3.client(
            's3',
            endpoint_url='http://localhost:9000',
            aws_access_key_id='foodgram_minio',
            aws_secret_access_key='foodgram_minio_secure_password_123',
            region_name='us-east-1'
        )
        
        bucket_name = 'foodgram'
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' already exists")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Bucket doesn't exist, create it
                pass
            else:
                print(f"❌ Error checking bucket: {e}")
                return False
        
        # Create bucket
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' created successfully")
        
        # Set bucket policy to public read for static files
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/static/*"
                }
            ]
        }
        
        try:
            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=str(bucket_policy).replace("'", '"')
            )
            print(f"✅ Bucket policy set for '{bucket_name}'")
        except Exception as e:
            print(f"⚠️  Warning: Could not set bucket policy: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = create_minio_bucket()
    sys.exit(0 if success else 1) 