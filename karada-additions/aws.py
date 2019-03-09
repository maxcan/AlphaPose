import boto3
import re
from pathlib import Path
import os
import json
import requests
import datetime
import tempfile

if __name__ == "__main__":

    print("aws.py starting up v1025")
    print(os.environ)
    try:
        s3 = boto3.client('s3')
        # for bucket in s3.buckets.all():
        #     print(bucket.name)
        s3_key = os.environ['karada_s3_key']
        output_prefix = os.environ['karada_output_prefix']
        print('s3Key  = ' , s3_key)
        s3_key_path = Path(s3_key)
        with tempfile.TemporaryDirectory() as tmpdirname:
            print('created temporary directory', tmpdirname)
            path_root = Path(tmpdirname)
            tmp_path = path_root / s3_key_path.name
            output_path = path_root / output_prefix
            print('about to mk path ' , output_path)
            if (output_path.exists()): output_path.rmdir()
            output_path.mkdir(parents=True)
            print('tmp_path: ' , tmp_path)
            print('tmp_path exists?: ' , tmp_path.exists())
            print('s3_key_path: ' , s3_key_path)
            if (tmp_path.exists()): tmp_path.unlink()
            print('about to flag and download to: ' , tmp_path)
            s3_bucket = os.environ['karada_s3_bucket']
            # s3.put_object(Body=b'Started Processing Flag', Bucket=s3_bucket, Key=output_prefix + '/process_start_flag')
            s3.download_file(s3_bucket, s3_key, str(tmp_path))
            size = os.stat(str(tmp_path)).st_size
            print('downloaded ' , size , ' bytes.. running karada')
            os.environ['AP_ARGS_OVERRIDE'] = '--video ' + str(tmp_path) + ' --outdir ' + str(output_path) + ' --save_video --sp'
            from opt import  reload
            reload()

            import karada
            karada_run_frame_count = 0
            def on_frame_count(count):
                print('total frames ' + str(count))
                # a bit hackish..  
                global karada_run_frame_count
                karada_run_frame_count = count
            def on_iter(count):
                status = json.dumps({"total": karada_run_frame_count, "done": count, "date": datetime.datetime.now().isoformat()})
                s3.put_object(Body=status.encode('utf-8'), Bucket=s3_bucket, Key=output_prefix + '/progress.json')
                print(status)
            karada.run(on_iter=on_iter, on_frame_count=on_frame_count, report_batch_size=48)
            
            for root,dirs,files in os.walk(str(output_path)):
                for file in files:
                    print('DEBUG: file = ' + file + ' AND ROOT = ' + root)
                    full_file = os.path.join(root, file)
                    output_key  = output_prefix + '/' + file
                    output_key = re.sub("alphapose","pose", output_key, flags=re.IGNORECASE)
    
                    print('uploading ' + full_file + ' to ' + output_key)
                    s3.upload_file(os.path.join(root,file), s3_bucket , output_key)
            print('clearing')
            for root,dirs,files in os.walk(str(output_path)):
                for file in files:
                    full_file = os.path.join(root, file)
                    print('removing ' + full_file)
                    Path(full_file).unlink()
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
