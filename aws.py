import boto3
from pathlib import Path
import os
import requests

path_root = Path("/tmp")
if __name__ == "__main__":

    print("aws.py starting up v107")
    print(os.environ)
    try:
        s3 = boto3.client('s3')
        # for bucket in s3.buckets.all():
        #     print(bucket.name)
        s3_key = os.environ['karada_s3_key']
        output_uuid = os.environ['karada_output_uuid']
        print('s3Key  = ' , s3_key)
        s3_key_path = Path(s3_key)
        tmp_path = path_root / s3_key_path.name
        output_path = path_root / output_uuid
        print('about to mk path ' , output_path)
        if (output_path.exists()): output_path.rmdir()
        output_path.mkdir(parents=True)
        print('tmp_path: ' , tmp_path)
        print('tmp_path exists?: ' , tmp_path.exists())
        print('s3_key_path: ' , s3_key_path)
        if (tmp_path.exists()): tmp_path.unlink()
        print('about to download to: ' , tmp_path)
        s3_bucket = os.environ['karada_s3_bucket']
        s3.download_file(s3_bucket, s3_key, str(tmp_path))
        size = os.stat(tmp_path).st_size
        print('downloaded ' , size , ' bytes.. running karada')
        os.environ['AP_ARGS_OVERRIDE'] = '--video ' , str(tmp_path) , ' --outdir {str(output_path)} --save_video --sp'
        from opt import  reload
        reload()

        import karada
        karada.run()
        # video=str(tmp_path),
        #     mode="normal",
        #     outputpath=str(output_path),
        #     detbatch=1,
        #     fast_inference=True,
        #     dataset='coco',
        #     save_video=True, # save the rendered video
        #     posebatch=80,
        #     profile=False,
        #     save_img=False,
        #     vis_fast=False
        #     )

        for root,dirs,files in os.walk(output_path):
            for file in files:
                print('uploading {file} from {output_path}')
                s3.upload_file(os.path.join(root,file), s3_bucket , 'output/{output_uuid}/{file}')
        print('clearing')
        for root,dirs,files in os.walk(output_path):
            for file in files:
                print('removing {file} from {output_path}')
                Path(file).unlink()
        output_path.rmdir()
        tmp_path.unlink()
        print('done')

    except Exception as inst:
         print(type(inst))    # the exception instance
         print(inst)          # __str__ allows args to be printed directly,
         print('failed')

    #  f" nvidia-docker run -it --rm -v { video_dir }:/tmp/in/:ro"
    #  f" -v { output_path }:/tmp/out:rw"
    #  f" karada-alphapose:latest python3 video_demo.py 
    #      --video /tmp/in/{video_path.name} "
    #  f" --outdir /tmp/out/  --save_video --sp ")
