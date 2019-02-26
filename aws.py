import boto3
import os
import requests


print("aws.py starting up v107")
print(os.environ)

print('loading metadata')
req = requests.get(os.environ['ECS_CONTAINER_METADATA_URI'])
print(req.text)
# http://169.254.170.2/v3/d83e1eab-63ba-4ac4-ba6a-6156a0073971

try:
    print("plain s3")
    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)
    s3_key = os.environ['s3Key']
    print(f's3Key  = {s3_key}')
    s3_key_path = Path(s3_key)
    tmp_path = "/tmp/" / s3_key_path
    print(f'tmp_path: {tmp_path}')
    print(f'tmp_path exists?: {tmp_path.exists()}')
    print(f's3_key_path: {s3_key_path}')
    if (tmp_path.exists()): tmp_path.unlink()
    print(f'about to download to: {tmp_path}')
    s3_client.download_file(os.environ['s3Bucket'], s3Key, tmp_path)
    size = os.stat(tmp_path).st_size
    print(f'downloaded {size} bytes.. will delete')
    tmp_path.unlink()
    print(f'done')

except:
    print('failed')