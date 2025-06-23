#!/usr/bin/env python3
"""Script to create MinIO bucket for Foodgram static files."""

import boto3
from botocore.exceptions import ClientError
import sys
import json


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
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Create bucket if it doesn't exist
                s3_client.create_bucket(Bucket=bucket_name)
                print(f"✅ Bucket '{bucket_name}' created successfully")
            else:
                print(f"❌ Error checking bucket: {e}")
                return False
        
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
        
        # Always update bucket policy
        try:
            policy_json = json.dumps(bucket_policy)
            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=policy_json
            )
            print(f"✅ Bucket policy updated for '{bucket_name}'")
            print(f"📋 Policy: {policy_json}")
        except Exception as e:
            print(f"⚠️  Warning: Could not set bucket policy: {e}")
            
        # List static files to verify they exist
        try:
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix='static/',
                MaxKeys=5
            )
            if 'Contents' in response:
                print(f"✅ Found {len(response['Contents'])} static files in bucket")
                for obj in response['Contents'][:3]:
                    print(f"   📄 {obj['Key']}")
            else:
                print("⚠️  No static files found in bucket - run collectstatic")
        except Exception as e:
            print(f"⚠️  Could not list bucket contents: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = create_minio_bucket()
    sys.exit(0 if success else 1) 