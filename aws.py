import boto3
import os
import requests


if __name__ == "main":

    print("aws.py starting up v107")
    print(os.environ)
    try:
        s3 = boto3.resource('s3')
        # for bucket in s3.buckets.all():
        #     print(bucket.name)
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


    #  f" nvidia-docker run -it --rm -v { video_dir }:/tmp/in/:ro"
    #  f" -v { output_path }:/tmp/out:rw"
    #  f" karada-alphapose:latest python3 video_demo.py --video /tmp/in/{video_path.name} "
    #  f" --outdir /tmp/out/  --save_video --sp ")