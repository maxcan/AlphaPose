import boto3
import os
import requests
import karada

path_root = Path("/tmp")
if __name__ == "main":

    print("aws.py starting up v107")
    print(os.environ)
    try:
        s3 = boto3.resource('s3')
        # for bucket in s3.buckets.all():
        #     print(bucket.name)
        s3_key = os.environ['karada_s3_key']
        output_uuid = os.environ['karada_output_uuid']
        print(f's3Key  = {s3_key}')
        s3_key_path = Path(s3_key)
        tmp_path = path_root / s3_key_path
        output_path = path_root / output_uuid
        output_path.mkdir(parents=True)
        print(f'tmp_path: {tmp_path}')
        print(f'tmp_path exists?: {tmp_path.exists()}')
        print(f's3_key_path: {s3_key_path}')
        if (tmp_path.exists()): tmp_path.unlink()
        print(f'about to download to: {tmp_path}')
        s3_bucket = os.environ['karada_s3_bucket']
        s3_client.download_file(s3_bucket, s3Key, tmp_path)
        size = os.stat(tmp_path).st_size
        print(f'downloaded {size} bytes.. running karada')

        karada.run(video=str(tmp_path),
            mode="normal",
            outputpath=str(output_path),
            detbatch=1,
            fast_inference=True,
            save_video=True, # save the rendered video
            posebatch=80,
            profile=False,
            save_img=False,
            vis_fast=False
            )

        for root,dirs,files in os.walk(output_path):
            for file in files:
                print(f'uploading {file} from {output_path}')
                s3_client.upload_file(os.path.join(root,file), s3_bucket , f'output/{output_uuid}/{file}')
        print(f'clearing')
        output_path.rmdir()
        tmp_path.unlink()
        print(f'done')

    except:
        print('failed')


    #  f" nvidia-docker run -it --rm -v { video_dir }:/tmp/in/:ro"
    #  f" -v { output_path }:/tmp/out:rw"
    #  f" karada-alphapose:latest python3 video_demo.py 
    #      --video /tmp/in/{video_path.name} "
    #  f" --outdir /tmp/out/  --save_video --sp ")