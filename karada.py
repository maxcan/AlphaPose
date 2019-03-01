import torch
from torch.autograd import Variable
import torch.nn.functional as F
import torchvision.transforms as transforms

import torch.nn as nn
import torch.utils.data
import numpy as np
from opt import opt

from dataloader import VideoLoader, DetectionLoader, DetectionProcessor, DataWriter, Mscoco
from yolo.util import write_results, dynamic_write_results
from SPPE.src.main_fast_inference import *

import ntpath
import os
import sys
from tqdm import tqdm
import time
from fn import getTime
import cv2

from pPose_nms import pose_nms, write_json

# kwargs = opt
# kwargs['dataset'] = 'coco'
# if not kwargs['sp']:
#     torch.multiprocessing.set_start_method('forkserver', force=True)
#     torch.multiprocessing.set_sharing_strategy('file_system')

def run(**kwargs):
    print(f'Running karada {kwargs}')
    videofile = kwargs['video']
    mode = kwargs['mode']
    if not os.path.exists(kwargs['outputpath']):
        os.mkdir(kwargs['outputpath'])
    
    if not len(videofile):
        raise IOError('Error: must contain --video')

    # Load input video
    print('about to load vidoe')
    data_loader = VideoLoader(videofile, batchSize=kwargs['detbatch']).start()
    (fourcc,fps,frameSize) = data_loader.videoinfo()

    # Load detection loader
    print('Loading YOLO model..')
    sys.stdout.flush()
    det_loader = DetectionLoader(data_loader, batchSize=kwargs['detbatch']).start()
    det_processor = DetectionProcessor(det_loader).start()
    
    print('# Load pose model')
    pose_dataset = Mscoco()
    if kwargs['fast_inference']:
        pose_model = InferenNet_fast(4 * 1 + 1, pose_dataset)
    else:
        pose_model = InferenNet(4 * 1 + 1, pose_dataset)
    print('about to cuda')
    pose_model.cuda()
    pose_model.eval()

    runtime_profile = {
        'dt': [],
        'pt': [],
        'pn': []
    }

    print('about to write videos')
    # Data writer
    save_path = os.path.join(kwargs['outputpath'], 'AlphaPose_'+ntpath.basename(videofile).split('.')[0]+'.avi')
    writer = DataWriter(kwargs['save_video'], save_path, cv2.VideoWriter_fourcc(*'XVID'), fps, frameSize).start()

    im_names_desc =  range(data_loader.length())
    # im_names_desc =  tqdm(range(data_loader.length()))
    batchSize = kwargs['posebatch']
    for i in im_names_desc:
        start_time = getTime()
        with torch.no_grad():
            (inps, orig_img, im_name, boxes, scores, pt1, pt2) = det_processor.read()
            if orig_img is None:
                break
            if boxes is None or boxes.nelement() == 0:
                writer.save(None, None, None, None, None, orig_img, im_name.split('/')[-1])
                continue

            ckpt_time, det_time = getTime(start_time)
            runtime_profile['dt'].append(det_time)
            # Pose Estimation
            
            datalen = inps.size(0)
            leftover = 0
            if (datalen) % batchSize:
                leftover = 1
            num_batches = datalen // batchSize + leftover
            hm = []
            for j in range(num_batches):
                inps_j = inps[j*batchSize:min((j +  1)*batchSize, datalen)].cuda()
                hm_j = pose_model(inps_j)
                hm.append(hm_j)
            hm = torch.cat(hm)
            ckpt_time, pose_time = getTime(ckpt_time)
            runtime_profile['pt'].append(pose_time)

            hm = hm.cpu().data
            writer.save(boxes, scores, hm, pt1, pt2, orig_img, im_name.split('/')[-1])

            ckpt_time, post_time = getTime(ckpt_time)
            runtime_profile['pn'].append(post_time)

        if kwargs['profile']:
            # TQDM
            im_names_desc.set_description(
            'det time: {dt:.3f} | pose time: {pt:.2f} | post processing: {pn:.4f}'.format(
                dt=np.mean(runtime_profile['dt']), pt=np.mean(runtime_profile['pt']), pn=np.mean(runtime_profile['pn']))
            )

    print('===========================> Finish Model Running.')
    if (kwargs['save_img'] or kwargs['save_video']) and not kwargs['vis_fast']:
        print('===========================> Rendering remaining images in the queue...')
        print('===========================> If this step takes too long, you can enable the --vis_fast flag to use fast rendering (real-time).')
    while(writer.running()):
        pass
    writer.stop()
    final_result = writer.results()
    write_json(final_result, kwargs['outputpath'])
