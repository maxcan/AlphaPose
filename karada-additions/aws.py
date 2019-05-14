import boto3
import magic
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
            global results_md
            def on_metadata(video_md):
                # a bit hackish..  
                global karada_run_frame_count
                karada_run_frame_count = video_md['length']
                print('[on metadata] total frames:: ' + str(karada_run_frame_count))
                print('[on metadata] path: ' + tmp_path)
                content_type = magic.from_file(tmp_path, mime=True)
                video_md['content_type'] = content_type
                print('[on metadata] about to dump json')
                md = json.dumps(video_md)
                print('[on metadata] about to put_object')
                s3.put_object(Body=md.encode('utf-8'), Bucket=s3_bucket, Key=output_prefix + '/upload_metadata.json')
                magic.from_file("testdata/test.pdf")

                global results_md
                results_md = json.dumps({'fps': video_md['fps'],
                        'width': video_md['width'],
                        'height': video_md['height'],
                        'length': video_md['length'],
                        'content_type': 'video/mp4'})

            def on_iter(count):
                status = json.dumps({"total": karada_run_frame_count, "done": count, "date": datetime.datetime.now().isoformat()})
                s3.put_object(Body=status.encode('utf-8'), Bucket=s3_bucket, Key=output_prefix + '/progress.json')
                print(status)
            karada.run(on_iter=on_iter, on_metadata=on_metadata, report_batch_size=48, thumbnail_path=str(output_path / 'thumbnail.png'))
            
            print('[aws.py:74] output complete')
            # Output complete
            status = json.dumps({"total": karada_run_frame_count, "done": karada_run_frame_count, "date": datetime.datetime.now().isoformat()})
            s3.put_object(Body=status.encode('utf-8'), Bucket=s3_bucket, Key=output_prefix + '/progress.json')
            for root,dirs,files in os.walk(str(output_path)):
                for file in files:
                    print('DEBUG: file = ' + file + ' AND ROOT = ' + root)
                    full_file = os.path.join(root, file)
                    output_key  = output_prefix + '/' + file
                    output_key = re.sub("alphapose-","pose_", output_key, flags=re.IGNORECASE)
    
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
            print('Uploading results MD: ' + results_md)
            s3.put_object(Body=results_md.encode('utf-8'),
                    Bucket=s3_bucket,
                    Key=output_prefix + '/pose_basic.mp4_metadata.json')
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
